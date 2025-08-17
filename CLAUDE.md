# Project Memory - Public Repository

## Overview
This is dang's public repository containing scripts and configurations for personal infrastructure projects. The main focus is on IoT energy monitoring and data pipeline integration.

## Project Structure
```
/
├── README.md - Main project overview
├── LICENSE - Project license
├── development/
│   └── iotawatt/ - IoTaWatt energy monitoring scripts
│       ├── README.md - Detailed documentation for IoTaWatt integration
│       ├── Dockerfile - Container configuration
│       ├── requirements.txt - Python dependencies (datetime, requests)
│       ├── vm_iotawatt_sync.py - Ongoing data synchronization script
│       └── vm_iotawatt_transform.py - Data transformation script
└── k3s/ - Kubernetes configurations (currently empty)
```

## Key Components

### IoTaWatt Integration
- **Purpose**: Move data from IoTaWatt energy monitoring systems to VictoriaMetrics
- **Previous setup**: Was using InfluxDB, migrated to VictoriaMetrics
- **Data sources**: Two IoTaWatt units monitoring electrical panel
  - iwatt5: Main data points (trunks) - 14 measurements
  - iwatt6: Individual circuits - 14 measurements
- **Energy calculations**: Load = Mains_1 + Mains_2, Solar production tracking, Grid import/export
- **Resolution**: 1-minute data (downsampled from 5s recent + 1m historical)
- **Sync frequency**: Every 5 minutes

### Dependencies
- Python with `datetime` and `requests` libraries
- VictoriaMetrics server: `https://vms-prod-lt.goepp.net`
- Docker support via Dockerfile

## Git Status
- Current branch: main
- Recent commits focus on VM server migration and logging improvements
- Contains dockerization and long-running Python container support

## Development Notes
- Scripts are custom-built for this specific setup, not generic
- Historical data loading vs ongoing sync (separate scripts)
- Minimal impact on IoTaWatt units (includes sleep delays)
- Extra tagging for Grafana visualization
- Uses power data estimation rather than integrator-based energy calculations

## Future Plans
- Migrate more work to this public repository
- Clean up scripts and k8s configs for public presentation
- Potential collaboration on making scripts more generic/configurable