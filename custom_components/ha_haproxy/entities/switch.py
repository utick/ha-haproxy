from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import CONF_BACKEND, DEVICE_INFO_DEFAULT, DOMAIN
from ..coordinator import HAProxyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HAProxyCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    backend_name = config_entry.data.get(CONF_BACKEND)

    entities = []

    if coordinator.data:
        backend = coordinator.get_backend(backend_name) if backend_name else (
            coordinator.data.backends[0] if coordinator.data.backends else None
        )
        if backend:
            for server in backend.servers:
                entities.append(
                    HAProxyServerSwitch(
                        coordinator=coordinator,
                        backend_name=backend.name,
                        server_name=server.name,
                    )
                )

    async_add_entities(entities)


class HAProxyServerSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        coordinator: HAProxyCoordinator,
        backend_name: str,
        server_name: str,
    ) -> None:
        super().__init__(coordinator)
        self.backend_name = backend_name
        self.server_name = server_name
        self._attr_unique_id = f"{coordinator.api.host}-{backend_name}-{server_name}"
        self._attr_device_info = {
            **DEVICE_INFO_DEFAULT,
            "identifiers": {(DOMAIN, f"{coordinator.api.host}-{backend_name}")},
            "name": f"HAProxy {backend_name}",
        }
        self._attr_name = f"{server_name}"
        self._attr_icon = "mdi:server-network"

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        backend = self.coordinator.get_backend(self.backend_name)
        if not backend:
            return False
        for server in backend.servers:
            if server.name == self.server_name:
                return server.is_enabled
        return False

    async def async_turn_on(self) -> bool:
        return await self.coordinator.enable_server(self.backend_name, self.server_name)

    async def async_turn_off(self) -> bool:
        return await self.coordinator.disable_server(self.backend_name, self.server_name)
