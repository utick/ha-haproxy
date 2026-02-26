import logging
from typing import Optional

import aiohttp
from .const import (
    DEFAULT_PORT,
    DEFAULT_STATS_PATH,
    SERVER_STATUS_DOWN,
    SERVER_STATUS_MAINT,
    SERVER_STATUS_NOLB,
    SERVER_STATUS_UP,
)
from .types import HAProxyBackend, HAProxyServer, HAProxyStats

_LOGGER = logging.getLogger(__name__)


class HAProxyAPI:
    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        username: Optional[str] = None,
        password: Optional[str] = None,
        stats_path: str = DEFAULT_STATS_PATH,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.stats_path = stats_path
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def base_url(self) -> str:
        if self.username and self.password:
            return f"http://{self.username}:{self.password}@{self.host}:{self.port}{self.stats_path}"
        return f"http://{self.host}:{self.port}{self.stats_path}"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_stats(self) -> HAProxyStats:
        session = await self._get_session()
        url = f"{self.base_url};json"

        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to fetch HAProxy stats: %s", err)
            raise

        return self._parse_stats(data)

    def _parse_stats(self, data: list) -> HAProxyStats:
        stats = HAProxyStats()
        backends: dict[str, HAProxyBackend] = {}
        pending_servers: list[dict] = []
        
        for section in data:
            if not isinstance(section, list):
                continue
            
            pxname = None
            svname = None
            scur = 0
            smax = 0
            slim = 0
            qcur = 0
            qmax = 0
            status = "DOWN"
            weight = 0
            act = 0
            bck = 0
            chkfail = 0
            
            for item in section:
                if not isinstance(item, dict):
                    continue
                field_name = item.get("field", {}).get("name")
                value = item.get("value", {}).get("value")
                
                if field_name == "pxname":
                    pxname = value
                elif field_name == "svname":
                    svname = value
                elif field_name == "scur":
                    scur = int(value) if value else 0
                elif field_name == "smax":
                    smax = int(value) if value else 0
                elif field_name == "slim":
                    slim = int(value) if value else 0
                elif field_name == "qcur":
                    qcur = int(value) if value else 0
                elif field_name == "qmax":
                    qmax = int(value) if value else 0
                elif field_name == "status":
                    status = value if value else "DOWN"
                elif field_name == "weight":
                    weight = int(value) if value else 0
                elif field_name == "act":
                    act = int(value) if value else 0
                elif field_name == "bck":
                    bck = int(value) if value else 0
                elif field_name == "chkfail":
                    chkfail = int(value) if value else 0
            
            if not pxname:
                continue
            
            if svname == "FRONTEND":
                continue
            
            if svname == "BACKEND":
                backends[pxname] = HAProxyBackend(
                    name=pxname,
                    status=self._normalize_status(status),
                    scur=scur,
                    smax=smax,
                    slim=slim,
                    qcur=qcur,
                    qmax=qmax,
                    servers=[],
                )
                continue
            
            pending_servers.append({
                "pxname": pxname,
                "svname": svname,
                "status": status,
                "scur": scur,
                "qcur": qcur,
                "weight": weight,
                "act": act,
                "bck": bck,
                "chkfail": chkfail,
            })
        
        for server_data in pending_servers:
            pxname = server_data["pxname"]
            if pxname in backends:
                server = HAProxyServer(
                    name=server_data["svname"],
                    backend=pxname,
                    status=self._normalize_status(server_data["status"]),
                    scur=server_data["scur"],
                    qcur=server_data["qcur"],
                    weight=server_data["weight"],
                    act=server_data["act"],
                    bck=server_data["bck"],
                    chkfail=server_data["chkfail"],
                )
                backends[pxname].servers.append(server)

        stats.backends = list(backends.values())
        return stats

    def _normalize_status(self, status: str) -> str:
        if not status:
            return SERVER_STATUS_DOWN
        status_upper = status.upper()
        if status_upper.startswith("UP"):
            return SERVER_STATUS_UP
        if status_upper.startswith("DOWN"):
            return SERVER_STATUS_DOWN
        if "MAINT" in status_upper:
            return SERVER_STATUS_MAINT
        if "NOLB" in status_upper:
            return SERVER_STATUS_NOLB
        return status_upper

    async def enable_server(self, backend: str, server: str) -> bool:
        return await self._send_command(f"enable server {backend}/{server}")

    async def disable_server(self, backend: str, server: str) -> bool:
        return await self._send_command(f"disable server {backend}/{server}")

    async def _send_command(self, command: str) -> bool:
        session = await self._get_session()
        url = f"{self.base_url};cmd"

        try:
            async with session.post(url, data=command) as response:
                if response.status == 200:
                    _LOGGER.info("Command '%s' executed successfully", command)
                    return True
                else:
                    text = await response.text()
                    _LOGGER.error(
                        "Command '%s' failed with status %d: %s",
                        command,
                        response.status,
                        text,
                    )
                    return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to send command '%s': %s", command, err)
            return False
