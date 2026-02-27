from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import (
    ATTR_ACTIVE_SESSIONS_NODES,
    ATTR_CURRENT_CONNECTIONS,
    ATTR_CURRENT_QUEUE,
    ATTR_READY_NODES,
    ATTR_TOTAL_NODES,
    CONF_BACKEND,
    DEVICE_INFO_DEFAULT,
    DOMAIN,
)
from ..coordinator import HAProxyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HAProxyCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    backend_name = config_entry.data.get(CONF_BACKEND)

    entities = []

    entities.append(
        HAProxySensor(
            coordinator=coordinator,
            backend_name=backend_name,
            description=SensorEntityDescription(
                key=ATTR_READY_NODES,
                name="Ready Nodes",
                icon="mdi:server",
                native_unit_of_measurement="nodes",
            ),
        )
    )

    entities.append(
        HAProxySensor(
            coordinator=coordinator,
            backend_name=backend_name,
            description=SensorEntityDescription(
                key=ATTR_TOTAL_NODES,
                name="Total Nodes",
                icon="mdi:server-network",
                native_unit_of_measurement="nodes",
            ),
        )
    )

    entities.append(
        HAProxySensor(
            coordinator=coordinator,
            backend_name=backend_name,
            description=SensorEntityDescription(
                key=ATTR_ACTIVE_SESSIONS_NODES,
                name="Active Sessions Nodes",
                icon="mdi:account-multiple",
                native_unit_of_measurement="nodes",
            ),
        )
    )

    entities.append(
        HAProxySensor(
            coordinator=coordinator,
            backend_name=backend_name,
            description=SensorEntityDescription(
                key=ATTR_CURRENT_CONNECTIONS,
                name="Current Connections",
                icon="mdi:connection",
            ),
        )
    )

    entities.append(
        HAProxySensor(
            coordinator=coordinator,
            backend_name=backend_name,
            description=SensorEntityDescription(
                key=ATTR_CURRENT_QUEUE,
                name="Current Queue",
                icon="mdi:queue-first",
            ),
        )
    )

    async_add_entities(entities)


class HAProxySensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: HAProxyCoordinator,
        backend_name: str | None,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.backend_name = backend_name
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.api.host}-{backend_name}-{description.key}"
        self._attr_device_info = {
            **DEVICE_INFO_DEFAULT,
            "identifiers": {(DOMAIN, f"{coordinator.api.host}-{backend_name}")},
            "name": f"HAProxy {backend_name or 'Stats'}",
        }

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0

        backend = self._get_backend()
        if not backend:
            return 0

        key = self.entity_description.key

        if key == ATTR_READY_NODES:
            return backend.ready_nodes
        if key == ATTR_TOTAL_NODES:
            return backend.total_nodes
        if key == ATTR_ACTIVE_SESSIONS_NODES:
            return backend.active_sessions_nodes
        if key == ATTR_CURRENT_CONNECTIONS:
            return backend.scur
        if key == ATTR_CURRENT_QUEUE:
            return backend.qcur

        return 0

    def _get_backend(self):
        if self.backend_name:
            return self.coordinator.get_backend(self.backend_name)
        if self.coordinator.data.backends:
            return self.coordinator.data.backends[0]
        return None
