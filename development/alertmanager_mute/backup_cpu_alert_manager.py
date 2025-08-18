#!/usr/bin/env python3
"""
Backup CPU Alert Manager Script

This script manages CPU alert silences for backup windows.
Designed to run via cron at 4:00 AM for backup operations.

Usage:
    python backup_cpu_alert_manager.py start [duration_minutes]  # Create silence
    python backup_cpu_alert_manager.py stop                     # Remove all CPU silences
    python backup_cpu_alert_manager.py status                   # Show active silences
    
Example cron entries:
    # Start maintenance at 4:00 AM for 15 minutes
    0 4 * * * /usr/bin/python3 /path/to/backup_cpu_alert_manager.py start 15
    
    # Or use a single cron entry that runs for 15 minutes then exits
    0 4 * * * timeout 15m /usr/bin/python3 /path/to/backup_cpu_alert_manager.py monitor
"""

import requests
import sys
import time
import signal
from datetime import datetime, timezone, timedelta

ALERTMANAGER_URL = "https://alertmanager-prod.goepp.net/api/v2"


class BackupCPUAlertManager:
    def __init__(self):
        self.silence_id = None

    def create_silence(self, duration_minutes=15):
        """Create a silence for CPU-related alerts"""
        start_time = datetime.now(timezone.utc).isoformat()
        end_time = (
            datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        ).isoformat()

        headers = {"Content-Type": "application/json"}

        data = {
            "matchers": [
                {
                    "name": "alertname",
                    "value": ".*CPU.*|.*cpu.*|.*Cpu.*",
                    "isRegex": True,
                    "isEqual": True,
                }
            ],
            "startsAt": start_time,
            "endsAt": end_time,
            "createdBy": "Backup CPU Alert Manager",
            "comment": f"Automated backup CPU alert silence - {duration_minutes} minutes",
        }

        try:
            response = requests.post(
                f"{ALERTMANAGER_URL}/silences", headers=headers, json=data
            )
            if response.status_code in [200, 201]:
                self.silence_id = response.json().get("silenceID")
                print(f"✓ CPU alert silence created (ID: {self.silence_id})")
                print(f"  Duration: {duration_minutes} minutes")
                return self.silence_id
            else:
                print(f"✗ Error creating silence: HTTP {response.status_code}")
                print(f"  Response: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error: {e}")
            return None

    def remove_cpu_silences(self):
        """Remove all active CPU-related silences"""
        try:
            # Get all active silences
            response = requests.get(f"{ALERTMANAGER_URL}/silences")
            if response.status_code != 200:
                print(f"✗ Error fetching silences: HTTP {response.status_code}")
                return False

            silences = response.json()
            cpu_silences = [
                s
                for s in silences
                if s.get("status", {}).get("state") == "active"
                and any(
                    "cpu" in str(matcher.get("value", "")).lower()
                    for matcher in s.get("matchers", [])
                )
            ]

            if not cpu_silences:
                print("! No active CPU silences to remove")
                return True

            # Remove each CPU silence
            removed_count = 0
            for silence in cpu_silences:
                silence_id = silence.get("id")
                delete_response = requests.delete(
                    f"{ALERTMANAGER_URL}/silence/{silence_id}"
                )
                if delete_response.status_code in [200, 204]:
                    print(f"✓ Removed silence {silence_id}")
                    removed_count += 1
                else:
                    print(
                        f"✗ Failed to remove silence {silence_id}: HTTP {delete_response.status_code}"
                    )

            print(f"✓ Removed {removed_count} CPU silence(s)")
            return removed_count > 0

        except requests.exceptions.RequestException as e:
            print(f"✗ Network error: {e}")
            return False

    def show_status(self):
        """Show status of CPU-related silences"""
        try:
            response = requests.get(f"{ALERTMANAGER_URL}/silences")
            if response.status_code != 200:
                print(f"✗ Error fetching silences: HTTP {response.status_code}")
                return

            silences = response.json()
            cpu_silences = [
                s
                for s in silences
                if any(
                    "cpu" in str(matcher.get("value", "")).lower()
                    for matcher in s.get("matchers", [])
                )
            ]

            if not cpu_silences:
                print("! No CPU-related silences found")
                return

            print(f"CPU Silences ({len(cpu_silences)} found):")
            for silence in cpu_silences:
                state = silence.get("status", {}).get("state", "unknown")
                print(f"  ID: {silence.get('id')}")
                print(f"  State: {state}")
                print(f"  Comment: {silence.get('comment', 'N/A')}")
                print(f"  Created: {silence.get('createdAt')}")
                print(f"  Ends: {silence.get('endsAt')}")
                print(f"  Updated: {silence.get('updatedAt')}")
                print("  ---")

        except requests.exceptions.RequestException as e:
            print(f"✗ Network error: {e}")

    def monitor_mode(self, duration_minutes=15):
        """Run in monitor mode - create silence and wait for duration"""
        print(
            f"🔧 Starting backup CPU alert monitor mode for {duration_minutes} minutes..."
        )

        # Set up signal handler for clean exit
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, cleaning up...")
            self.remove_cpu_silences()
            sys.exit(0)

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        # Create silence
        if not self.create_silence(duration_minutes):
            print("❌ Failed to create silence, exiting")
            sys.exit(1)

        print(f"⏱️  Monitoring for {duration_minutes} minutes...")
        print("   Press Ctrl+C to stop early")

        try:
            # Wait for the duration
            time.sleep(duration_minutes * 60)
            print("⏰ Backup window complete")
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        finally:
            # Clean up
            print("🧹 Removing CPU silences...")
            self.remove_cpu_silences()
            print("✅ Backup complete")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print(
            "Usage: backup_cpu_alert_manager.py {start|stop|status|monitor} [duration_minutes]"
        )
        print("\nCommands:")
        print("  start [duration]  - Create CPU alert silence (default: 15 min)")
        print("  stop              - Remove all CPU alert silences")
        print("  status            - Show status of CPU silences")
        print("  monitor [duration]- Run maintenance mode (create, wait, cleanup)")
        sys.exit(1)

    command = sys.argv[1].lower()
    manager = BackupCPUAlertManager()

    if command == "start":
        duration = 15
        if len(sys.argv) > 2:
            try:
                duration = int(sys.argv[2])
                if duration <= 0:
                    print("Duration must be positive")
                    sys.exit(1)
            except ValueError:
                print("Duration must be a valid integer")
                sys.exit(1)

        result = manager.create_silence(duration)
        sys.exit(0 if result else 1)

    elif command == "stop":
        result = manager.remove_cpu_silences()
        sys.exit(0 if result else 1)

    elif command == "status":
        manager.show_status()

    elif command == "monitor":
        duration = 15
        if len(sys.argv) > 2:
            try:
                duration = int(sys.argv[2])
                if duration <= 0:
                    print("Duration must be positive")
                    sys.exit(1)
            except ValueError:
                print("Duration must be a valid integer")
                sys.exit(1)

        manager.monitor_mode(duration)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
