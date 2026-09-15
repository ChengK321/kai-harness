"""Local read-only collection: uname, procfs and filesystem capacity only."""

import math
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from .models import Capacity, RawObservation


def _cpu_ticks() -> tuple[int, int]:
    with Path("/proc/stat").open("r", encoding="ascii") as stream:
        fields = stream.readline().split()
    if not fields or fields[0] != "cpu" or len(fields) < 5:
        raise ValueError("Invalid CPU counters")
    # guest/guest_nice are already included in user/nice; do not double count.
    values = [int(value) for value in fields[1:9]]
    if any(value < 0 for value in values):
        raise ValueError("Negative CPU counters")
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    return sum(values), idle


def _cpu_percent(interval: float) -> float:
    total_before, idle_before = _cpu_ticks()
    time.sleep(interval)
    total_after, idle_after = _cpu_ticks()
    total, idle = total_after - total_before, idle_after - idle_before
    if total <= 0 or idle < 0 or idle > total:
        raise ValueError("Invalid CPU sample delta")
    return (total - idle) / total * 100


def _capacity(total: int, used: int) -> Capacity:
    if total <= 0 or not 0 <= used <= total:
        raise ValueError("Invalid capacity counters")
    return Capacity(total, used)


def _memory() -> Capacity:
    values = {}
    with Path("/proc/meminfo").open("r", encoding="ascii") as stream:
        for line in stream:
            fields = line.split()
            if fields and fields[0] in ("MemTotal:", "MemAvailable:"):
                if len(fields) != 3 or fields[2] != "kB":
                    raise ValueError("Invalid memory units")
                values[fields[0]] = int(fields[1]) * 1024
    total = values["MemTotal:"]
    return _capacity(total, total - values["MemAvailable:"])


def _disk() -> Capacity:
    usage = shutil.disk_usage("/")
    return _capacity(usage.total, usage.used)


class VPSObserver:
    """Observe the local Linux host. environment_id is a label, never a target."""

    def __init__(self, sample_interval: float = 0.1):
        if not math.isfinite(sample_interval) or not 0 < sample_interval <= 1:
            raise ValueError("sample_interval must be finite and in (0, 1] seconds")
        self.sample_interval = sample_interval

    def collect(self, environment_id: str) -> RawObservation:
        if not isinstance(environment_id, str) or not environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        raw = RawObservation(environment_id=environment_id, timestamp="")
        collectors = {
            "hostname": lambda: os.uname().nodename,
            "os": lambda: os.uname().sysname,
            "kernel": lambda: os.uname().release,
            "cpu": lambda: _cpu_percent(self.sample_interval),
            "memory": _memory,
            "disk": _disk,
        }
        for field, collector in collectors.items():
            try:
                setattr(raw, field, collector())
            except (OSError, ValueError, KeyError, IndexError, UnicodeError, AttributeError):
                # Do not expose exception text, host paths or secrets in the contract.
                raw.errors.append({
                    "section": "system",
                    "code": f"{field.upper()}_UNAVAILABLE",
                    "message": f"Unable to collect {field}.",
                })
        raw.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return raw
