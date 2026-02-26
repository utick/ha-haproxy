from datetime import timedelta
import logging
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import HAProxyAPI
from .const import DEFAULT_SCAN_INTERVAL
from .types import HAProxyBackend, HAProxyStats

_LOGGER = logging.getLogger(__name__)


class HAProxyCoordinator(DataUpdateCoordinator[HAProxyStats]):
    def __init__(
        self,
        hass: HomeAssistant,
        api: HAProxyAPI,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ):
        super().__init__(
            hass,
            _LOGGER,
            name="HAProxy",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> HAProxyStats:
        try:
            return await self.api.get_stats()
        except Exception as err:
            raise

    def get_backend(self, name: str) -> Optional[HAProxyBackend]:
        if self.data:
            return self.data.get_backend(name)
        return None

    async def enable_server(self, backend: str, server: str) -> bool:
        result = await self.api.enable_server(backend, server)
        if result:
            await self.async_refresh()
        return result

    async def disable_server(self, backend: str, server: str) -> bool:
        result = await self.api.disable_server(backend, server)
        if result:
            await self.async_refresh()
        return result
