# HAProxy for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/utick/ha-haproxy)](https://github.com/utick/ha-haproxy/releases)
[![HACS validated](https://img.shields.io/badge/HACS-Validated-blue)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/utick/ha-haproxy)](LICENSE)

Home Assistant integration for monitoring and controlling [HAProxy](https://www.haproxy.org/) load balancer.

## Features

- **Sensors**: Monitor HAProxy backend statistics
  - Ready Nodes
  - Total Nodes
  - Active Sessions
  - Current Connections
  - Current Queue

- **Switches**: Control backend servers
  - Enable/Disable individual servers

## Installation

### Option 1: HACS (Recommended)

1. Add this repository via HACS
2. Search for "HAProxy" and install
3. Restart Home Assistant

### Option 2: Manual

Copy the `custom_components/ha_haproxy` folder to your Home Assistant's `custom_components` folder.

## Configuration

### YAML Configuration

Add the following to your `configuration.yaml`:

```yaml
ha_haproxy:
  - host: 192.168.1.100
    port: 8404
    stats_path: /stats
    # Optional: Authentication
    # username: admin
    # password: password
    # Optional: Specific backend to monitor
    # backend: my_backend
    # Optional: Scan interval in seconds (default: 30)
    # scan_interval: 30
```

### Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `host` | string | Yes | - | HAProxy stats URI or IP |
| `port` | integer | No | 8404 | HAProxy stats port |
| `stats_path` | string | No | /stats | Stats URL path |
| `username` | string | No | - | Basic auth username |
| `password` | string | No | - | Basic auth password |
| `backend` | string | No | - | Specific backend name to monitor |
| `scan_interval` | integer | No | 30 | Update interval in seconds |

## HAProxy Configuration

Enable the stats page in your HAProxy configuration:

```haproxy
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    # Optional: enable auth
    # stats auth admin:password
```

## Support

- Issues: https://github.com/utick/ha-haproxy/issues
- Discussions: https://github.com/utick/ha-haproxy/discussions

## License

MIT License - see [LICENSE](LICENSE) for details.
