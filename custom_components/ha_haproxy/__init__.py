import logging

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .api import HAProxyAPI
from .const import (
    CONF_BACKEND,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_STATS_PATH,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_STATS_PATH,
    DOMAIN,
)
from .coordinator import HAProxyCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(cv.ensure_list, [
        {
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
            vol.Optional(CONF_STATS_PATH, default=DEFAULT_STATS_PATH): cv.string,
            vol.Optional(CONF_USERNAME): cv.string,
            vol.Optional(CONF_PASSWORD): cv.string,
            vol.Optional(CONF_BACKEND): cv.string,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
        }
    ])
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up HAProxy integration using YAML configuration."""
    
    ha_proxies = config.get(DOMAIN, [])
    
    if not ha_proxies:
        return True
        
    for ha_proxy_config in ha_proxies:
        host = ha_proxy_config[CONF_HOST]
        port = ha_proxy_config.get(CONF_PORT, DEFAULT_PORT)
        username = ha_proxy_config.get(CONF_USERNAME)
        password = ha_proxy_config.get(CONF_PASSWORD)
        stats_path = ha_proxy_config.get(CONF_STATS_PATH, DEFAULT_STATS_PATH)
        backend = ha_proxy_config.get(CONF_BACKEND)
        scan_interval = ha_proxy_config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        
        _LOGGER.info(f"Setting up HAProxy: {host}:{port}")
        
        api = HAProxyAPI(
            host=host,
            port=port,
            username=username,
            password=password,
            stats_path=stats_path,
        )
        
        coordinator = HAProxyCoordinator(
            hass=hass,
            api=api,
            scan_interval=scan_interval,
        )
        
        try:
            await coordinator.async_refresh()
        except Exception as e:
            _LOGGER.error(f"Failed to connect to HAProxy {host}:{port}: {e}")
            continue
        
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][f"{host}:{port}"] = coordinator
        
        sensor_info = [
            ('ready_nodes', 'Ready Nodes', 'mdi:server', 'nodes'),
            ('total_nodes', 'Total Nodes', 'mdi:server-network', 'nodes'),
            ('active_sessions_nodes', 'Active Sessions Nodes', 'mdi:account-multiple', 'nodes'),
            ('current_connections', 'Current Connections', 'mdi:connection', None),
            ('current_queue', 'Current Queue', 'mdi:queue-first', None),
        ]
        
        for key, name, icon, unit in sensor_info:
            entity_id = f"ha_haproxy_{host.replace('.', '_').replace('-', '_')}_{key}"
            hass.states.async_set(
                f"sensor.{entity_id}",
                0,
                {
                    "unique_id": f"{host}-{backend or 'default'}-{key}",
                    "device_info": {
                        "identifiers": {(DOMAIN, f"{host}-{backend}")},
                        "name": f"HAProxy {backend or host}",
                        "manufacturer": "HAProxy",
                        "model": "Load Balancer",
                    },
                    "icon": icon,
                    "unit_of_measurement": unit,
                    "friendly_name": name,
                }
            )
        
        def _update_sensors():
            if not coordinator.data:
                return
            be = coordinator.get_backend(backend) if backend else (
                coordinator.data.backends[0] if coordinator.data.backends else None
            )
            if not be:
                return
            
            for key, name, icon, unit in sensor_info:
                value = 0
                if key == 'ready_nodes':
                    value = be.ready_nodes
                elif key == 'total_nodes':
                    value = be.total_nodes
                elif key == 'active_sessions_nodes':
                    value = be.active_sessions_nodes
                elif key == 'current_connections':
                    value = be.scur
                elif key == 'current_queue':
                    value = be.qcur
                
                entity_id = f"ha_haproxy_{host.replace('.', '_').replace('-', '_')}_{key}"
                hass.states.async_set(
                    f"sensor.{entity_id}",
                    value,
                    {"unit_of_measurement": unit}
                )
        
        coordinator.async_add_listener(_update_sensors)
        _update_sensors()
        
        _LOGGER.info(f"HAProxy {host}:{port} sensors added")
        
    return True
