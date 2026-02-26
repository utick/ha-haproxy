from dataclasses import dataclass
from typing import Optional

from .const import (
    SERVER_STATUS_DOWN,
    SERVER_STATUS_MAINT,
    SERVER_STATUS_NOLB,
    SERVER_STATUS_UP,
)


@dataclass
class HAProxyServer:
    name: str
    backend: str
    status: str
    scur: int
    qcur: int
    weight: int
    act: int
    bck: int
    chkfail: int

    @property
    def is_ready(self) -> bool:
        return self.status == SERVER_STATUS_UP

    @property
    def is_maintenance(self) -> bool:
        return self.status == SERVER_STATUS_MAINT

    @property
    def has_sessions(self) -> bool:
        return self.scur > 0

    @property
    def is_enabled(self) -> bool:
        return self.status not in (SERVER_STATUS_MAINT, SERVER_STATUS_DOWN)


@dataclass
class HAProxyBackend:
    name: str
    status: str
    scur: int
    smax: int
    slim: int
    qcur: int
    qmax: int
    servers: list[HAProxyServer]

    @property
    def total_nodes(self) -> int:
        return len(self.servers)

    @property
    def ready_nodes(self) -> int:
        return sum(1 for s in self.servers if s.is_ready)

    @property
    def active_sessions_nodes(self) -> int:
        return sum(1 for s in self.servers if s.has_sessions)


@dataclass
class HAProxyStats:
    hostname: Optional[str] = None
    version: Optional[str] = None
    backends: Optional[list[HAProxyBackend]] = None

    def __post_init__(self):
        if self.backends is None:
            self.backends = []

    def get_backend(self, name: str) -> Optional[HAProxyBackend]:
        if not self.backends:
            return None
        for backend in self.backends:
            if backend.name == name:
                return backend
        return None
