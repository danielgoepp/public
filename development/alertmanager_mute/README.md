# Backup CPU Alert Silence

Automated CPU alert silencing for backup windows using Alertmanager API.

## Backup CPU Alert Scripts

Two scripts are provided for managing CPU alert silences during backup windows:

### backup_cpu_alert_silence.py
Simple script to create a CPU alert silence for a specified duration.

```bash
# Create 15-minute silence (default)
python backup_cpu_alert_silence.py

# Create 30-minute silence
python backup_cpu_alert_silence.py 30
```

### backup_cpu_alert_manager.py
Advanced script with multiple modes for comprehensive backup alert management.

```bash
# Create CPU alert silence
python backup_cpu_alert_manager.py start [duration_minutes]

# Remove all CPU alert silences
python backup_cpu_alert_manager.py stop

# Check status of CPU silences
python backup_cpu_alert_manager.py status

# Monitor mode - create silence, wait, then cleanup
python backup_cpu_alert_manager.py monitor [duration_minutes]
```

## Deployment Options

### K3s/Kubernetes CronJob (Recommended)

The scripts are containerized and deployed as a Kubernetes CronJob:

```bash
# Deploy using build script (builds multi-platform image and deploys)
./build-and-deploy.sh

# Or deploy manually
kubectl apply -f backup-cpu-alert-cronjob.yaml

# Check status
kubectl get cronjobs -n management
kubectl get jobs --selector=app=backup-cpu-alert -n management

# View logs
kubectl logs -l app=backup-cpu-alert -n management --tail=50
```

### Docker Hub Image

Pre-built multi-platform image available:
- **Image**: `danielgoepp/backup-cpu-alert:latest`
- **Platforms**: linux/amd64, linux/arm64
- **Updated**: August 18, 2025

### Traditional Cron Usage

```bash
# Run at 4:00 AM daily for 15 minutes
0 4 * * * cd /path/to/grafana && python3 backup_cpu_alert_manager.py monitor 15
```

## Configuration

The scripts use the existing Alertmanager configuration:
- **URL**: `https://alertmanager-prod.goepp.net/api/v2`
- **Authentication**: No API key required for Alertmanager API
- **Target**: CPU-related alerts (matches alertname containing "CPU", "cpu", or "Cpu")

## Features

- **Regex matching**: Silences all CPU-related alerts using regex patterns
- **Automatic cleanup**: Monitor mode automatically removes silences when done
- **Signal handling**: Graceful shutdown with Ctrl+C
- **Status reporting**: Check active silences and their status
- **Error handling**: Comprehensive error reporting and status codes

## Container Files

- **Dockerfile** - Python 3.11 slim base (single script deployment)
- **requirements.txt** - Python dependencies (requests==2.31.0)
- **backup-cpu-alert-cronjob.yaml** - Kubernetes CronJob manifest (management namespace)
- **build-and-deploy.sh** - Multi-platform build and deployment script

## Testing

### Local Testing
```bash
# Test creating a 1-minute silence
python backup_cpu_alert_manager.py start 1

# Check it was created
python backup_cpu_alert_manager.py status

# Remove it manually
python backup_cpu_alert_manager.py stop
```

### Container Testing
```bash
# Build and test container locally
docker build -t backup-cpu-alert:latest .
docker run --rm backup-cpu-alert:latest python3 backup_cpu_alert_silence.py 1

# Test multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t danielgoepp/backup-cpu-alert:latest --push .
```

### K3s Testing
```bash
# Create a test job to run immediately
kubectl create job --from=cronjob/backup-cpu-alert-silence backup-test -n management
kubectl logs job/backup-test -n management
kubectl delete job backup-test -n management
```

## Deployment Status

✅ **Active Deployment**
- CronJob: `backup-cpu-alert-silence` in `management` namespace
- Schedule: Daily at 4:00 AM EST
- Duration: 15 minutes
- Last Updated: August 18, 2025