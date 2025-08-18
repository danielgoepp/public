# Backup CPU Alert Silence Project

## Project Overview
Scripts and container deployment for automatically silencing CPU-related alerts in Alertmanager during backup windows (4:00 AM - 4:15 AM daily).

## Problem Solved
During daily backups at 4:00 AM, CPU usage spikes cause false alerts. These scripts create temporary silences in Alertmanager to suppress CPU alerts during the 15-minute backup window.

## Solution Architecture
- **Python script** for Alertmanager API interaction (simple silence creation)
- **Docker Hub hosted container** for easy deployment
- **Kubernetes CronJob** for automated scheduling in K3s management namespace
- **15-minute silence window** with automatic expiration

## Files Created

### Core Scripts
- `backup_cpu_alert_silence.py` - Simple silence creation script (containerized)
- `backup_cpu_alert_manager.py` - Full management script (local use only)

### Container Deployment
- `Dockerfile` - Python 3.11 slim base with non-root user (only includes silence script)
- `requirements.txt` - Python dependencies (requests==2.31.0)
- `backup-cpu-alert-cronjob.yaml` - K3s CronJob manifest (management namespace)
- `build-and-deploy.sh` - Multi-platform build and deployment script
- `README.md` - Complete documentation

## Script Features
- **Regex matching** - Silences alerts with "CPU", "cpu", or "Cpu" in alertname
- **Automatic cleanup** - Monitor mode removes silences after duration
- **Error handling** - Comprehensive error reporting and HTTP status handling
- **Signal handling** - Graceful shutdown with Ctrl+C
- **Status reporting** - Check active silences and their status

## API Integration
- **Alertmanager URL**: `https://alertmanager-prod.goepp.net/api/v2`
- **No authentication** required for Alertmanager silences API
- **JSON payloads** with regex matchers for CPU alerts

## Deployment Details
- **Schedule**: 4:00 AM daily (`0 4 * * *`)
- **Duration**: 15 minutes (fixed)
- **Timezone**: America/New_York (configured in CronJob)
- **Namespace**: management
- **Resources**: 128Mi memory limit, 100m CPU limit
- **Concurrency**: Forbidden (no overlapping runs)
- **Job History**: 1 successful, 1 failed job retained

## Docker Hub Integration
- **Public image**: `danielgoepp/backup-cpu-alert:latest`
- **Multi-platform support**: linux/amd64, linux/arm64
- **Direct K3s deployment** from Docker Hub
- **No local registry** required

## Usage Commands
```bash
# Deploy to K3s management namespace
./build-and-deploy.sh

# Or manual deployment
kubectl apply -f backup-cpu-alert-cronjob.yaml

# Test immediately
kubectl create job --from=cronjob/backup-cpu-alert-silence backup-test -n management

# Check status
kubectl get cronjobs -n management
kubectl logs -l app=backup-cpu-alert -n management --tail=50

# Build and push new multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 -t danielgoepp/backup-cpu-alert:latest --push .

# Manual script usage (local)
python3 backup_cpu_alert_manager.py monitor 15
python3 backup_cpu_alert_silence.py 15
```

## Class and Function Names
- `BackupCPUAlertManager` - Main management class
- `create_silence()` - Creates Alertmanager silence
- `remove_cpu_silences()` - Removes active CPU silences
- `show_status()` - Displays silence status
- `monitor_mode()` - Runs full cycle with cleanup

## Configuration
- **Default duration**: 15 minutes
- **Alert pattern**: `.*CPU.*|.*cpu.*|.*Cpu.*` (regex)
- **Comment template**: "Automated backup CPU alert silence - X minutes"
- **Created by**: "Backup CPU Alert Manager"

## Deployment Status
- ✅ **Deployed**: August 18, 2025
- ✅ **CronJob Active**: backup-cpu-alert-silence in management namespace
- ✅ **Image Available**: danielgoepp/backup-cpu-alert:latest (multi-platform)
- ✅ **Schedule**: Daily at 4:00 AM EST
- ✅ **Test Successful**: 15-minute silence created and verified

## Migration Notes
When moving this code:
1. Update Alertmanager URL if different environment
2. Adjust timezone in CronJob manifest
3. Ensure management namespace exists in K3s
4. Verify K3s cluster access and kubectl context
5. Update Docker Hub image if modifications needed

## Current Location
`/Users/dang/Documents/Development/public/development/alertmanager_mute/`

## Dependencies
- Python 3.11+
- requests library
- Docker with buildx for multi-platform builds
- kubectl for K3s deployment
- Access to Alertmanager API endpoint
- Docker Hub account (danielgoepp)
- K3s management namespace

## Security Considerations
- Container runs as non-root user
- No credentials stored in container (Alertmanager API is unauthenticated)
- Resource limits prevent resource exhaustion
- Scripts have proper error handling and timeouts