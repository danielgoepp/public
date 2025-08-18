#!/usr/bin/env python3
"""
Backup CPU Alert Silence Script

This script creates a silence in Alertmanager for CPU-related alerts during
backup windows (e.g., 4:00 AM - 4:15 AM for backups).

Usage:
    python backup_cpu_alert_silence.py [duration_minutes]

If no duration is provided, defaults to 15 minutes.
"""

import requests
import sys
from datetime import datetime, timezone, timedelta

ALERTMANAGER_URL = "https://alertmanager-prod.goepp.net/api/v2"


def create_cpu_silence(duration_minutes=15):
    """Create a silence for CPU-related alerts"""
    start_time = datetime.now(timezone.utc).isoformat()
    end_time = (
        datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
    ).isoformat()

    headers = {"Content-Type": "application/json"}

    # Create silence for CPU-related alerts
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
        "createdBy": "Backup CPU Alert Script",
        "comment": f"Backup CPU alert silence - {duration_minutes} minute silence for CPU alerts",
    }

    try:
        response = requests.post(
            f"{ALERTMANAGER_URL}/silences", headers=headers, json=data
        )
        if response.status_code in [200, 201]:
            silence_id = response.json().get("silenceID")
            print(f"✓ CPU alert silence created successfully")
            print(f"  Silence ID: {silence_id}")
            print(f"  Duration: {duration_minutes} minutes")
            print(f"  Start: {start_time}")
            print(f"  End: {end_time}")
            return silence_id
        else:
            print(f"✗ Error creating silence: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return None


def list_active_silences():
    """List all active silences to verify our silence is active"""
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/silences")
        if response.status_code == 200:
            silences = response.json()
            active_cpu_silences = [
                s
                for s in silences
                if s.get("status", {}).get("state") == "active"
                and any(
                    "cpu" in str(matcher.get("value", "")).lower()
                    for matcher in s.get("matchers", [])
                )
            ]

            if active_cpu_silences:
                print(f"\n✓ Found {len(active_cpu_silences)} active CPU silence(s):")
                for silence in active_cpu_silences:
                    print(f"  ID: {silence.get('id')}")
                    print(f"  Comment: {silence.get('comment')}")
                    print(f"  Ends: {silence.get('endsAt')}")
            else:
                print("\n! No active CPU silences found")
        else:
            print(f"✗ Error fetching silences: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error fetching silences: {e}")


def main():
    """Main function"""
    duration = 15  # Default 15 minutes

    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
            if duration <= 0:
                print("Duration must be a positive integer")
                sys.exit(1)
        except ValueError:
            print("Duration must be a valid integer (minutes)")
            sys.exit(1)

    print(f"Creating CPU alert silence for {duration} minutes...")

    silence_id = create_cpu_silence(duration)

    if silence_id:
        print(f"\n🔇 CPU alerts silenced for {duration} minutes")
        list_active_silences()
    else:
        print("\n❌ Failed to create CPU alert silence")
        sys.exit(1)


if __name__ == "__main__":
    main()
