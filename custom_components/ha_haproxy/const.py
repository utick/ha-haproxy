from typing import Final

DOMAIN: Final = "ha_haproxy"

DEFAULT_PORT: Final = 8404
DEFAULT_STATS_PATH: Final = "/stats"
DEFAULT_SCAN_INTERVAL: Final = 30

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_STATS_PATH: Final = "stats_path"
CONF_BACKEND: Final = "backend"
CONF_SCAN_INTERVAL: Final = "scan_interval"

SERVER_STATUS_UP: Final = "UP"
SERVER_STATUS_DOWN: Final = "DOWN"
SERVER_STATUS_MAINT: Final = "MAINT"
SERVER_STATUS_NOLB: Final = "NOLB"
SERVER_STATUS_DRAIN: Final = "DRAIN"

ATTR_READY_NODES: Final = "ready_nodes"
ATTR_TOTAL_NODES: Final = "total_nodes"
ATTR_ACTIVE_SESSIONS_NODES: Final = "active_sessions_nodes"
ATTR_CURRENT_CONNECTIONS: Final = "current_connections"
ATTR_CURRENT_QUEUE: Final = "current_queue"

DEVICE_INFO_DEFAULT: Final = {
    "manufacturer": "HAProxy",
    "model": "Load Balancer",
}
