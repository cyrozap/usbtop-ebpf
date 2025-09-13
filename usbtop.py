#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD

# Copyright (C) 2025 by Forest Crossman <cyrozap@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
# PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import argparse
import time
from typing import NamedTuple

import bcc  # type: ignore[import-untyped]

ENDPOINT_TYPES: dict[int, str] = {
    0: "CTRL",
    1: "ISOC",
    2: "BULK",
    3: "INTR",
}


class DeviceKey(NamedTuple):
    """A key representing a single USB device."""

    busnum: int
    devnum: int
    vendor: int
    product: int

class EndpointKey(NamedTuple):
    """A key representing a single USB endpoint."""

    busnum: int
    devnum: int
    vendor: int
    product: int
    endpoint: int
    type: int

    def device_key(self) -> DeviceKey:
        """Get the device key for this endpoint."""
        return DeviceKey(busnum=self.busnum, devnum=self.devnum, vendor=self.vendor, product=self.product)

    def number(self) -> int:
        """Get the endpoint number."""
        return self.endpoint & 0x7F

    def is_in(self) -> bool:
        """Get the endpoint direction (True for IN, False for OUT)."""
        return (self.endpoint & 0x80) != 0


def format_speed(value_bytes: float, *, use_bits: bool = False) -> str:
    """Format a speed in bytes/sec into a human-readable string."""
    speed: float = value_bytes
    units: list[str] = ["B/s", "KiB/s", "MiB/s", "GiB/s", "TiB/s"]
    divisor: float = 1024.0
    if use_bits:
        speed = value_bytes * 8
        units = ["bps", "Kbps", "Mbps", "Gbps", "Tbps"]
        divisor = 1000.0

    unit_index: int = 0
    while speed >= divisor and unit_index < len(units) - 1:
        speed /= divisor
        unit_index += 1

    return f"{speed:.2f} {units[unit_index]}"

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bus", type=int, default=0,
                        help="The bus to measure traffic on. Default: 0 (all buses)")
    parser.add_argument("-i", "--interval", type=float, default=0.25,
                        help="The refresh interval in seconds. Default: 0.25")
    parser.add_argument("-t", "--timeout", type=int, default=5,
                        help="Seconds before an inactive device is removed. Default: 5")
    return parser.parse_args()

def display_stats(
    args: argparse.Namespace,
    known_endpoints: set[EndpointKey],
    traffic_data: dict[EndpointKey, int],
) -> None:
    """Display the USB traffic statistics."""
    sorted_keys: list[EndpointKey] = sorted(known_endpoints, key=lambda k: (k.busnum, k.devnum, k.number(), k.is_in()))

    output_lines: list[str] = []
    last_bus_key: int | None = None
    last_device_key: DeviceKey | None = None
    for key in sorted_keys:
        traffic_bytes: int = traffic_data.get(key, 0)

        if args.bus in (0, key.busnum):
            bus_key: int = key.busnum
            if bus_key != last_bus_key:
                output_lines.append(f"Bus {bus_key}:")
                last_bus_key = bus_key
                last_device_key = None

            device_key: DeviceKey = key.device_key()
            if device_key != last_device_key:
                bus_dev: str = f"{key.busnum:>3}.{key.devnum:<3}"
                vid_pid: str = f"[{key.vendor:04x}:{key.product:04x}]"
                output_lines.append(f"  Device {bus_dev} {vid_pid}:")
                last_device_key = device_key

            rate_bytes_per_sec: float = traffic_bytes / args.interval
            speed_bits: str = format_speed(rate_bytes_per_sec, use_bits=True)
            speed_bytes: str = format_speed(rate_bytes_per_sec, use_bits=False)
            endpoint: str = f"0x{key.endpoint:02x}"
            ep_type: str = ENDPOINT_TYPES.get(key.type, "UNKN")
            ep_dir: str = "IN" if key.is_in() else "OUT"
            output_lines.append(f"    {endpoint} ({ep_type}, {ep_dir:<3}): {speed_bits:>15} {speed_bytes:>15}")

    print("\033[2J\033[H" + "\n".join(output_lines), flush=True)

def main() -> None:
    """Run the usbtop tool."""
    args: argparse.Namespace = parse_args()

    b: bcc.BPF = bcc.BPF(src_file="perf.c")

    print("Tracing USB transfers... Hit Ctrl-C to end.")

    known_endpoints: set[EndpointKey] = set()
    device_last_seen: dict[DeviceKey, float] = {}
    try:
        while True:
            time.sleep(args.interval)

            stats: bcc.table.Table = b.get_table("stats")
            traffic_data: dict[EndpointKey, int] = {}
            now: float = time.monotonic()
            for k, v in stats.items():
                key: EndpointKey = EndpointKey(busnum=k.busnum, devnum=k.devnum, vendor=k.vendor, product=k.product, endpoint=k.endpoint, type=k.type)
                known_endpoints.add(key)
                traffic_data[key] = v.value
                device_key: DeviceKey = key.device_key()
                device_last_seen[device_key] = now

            timed_out_devices: set[DeviceKey] = {dev_key for dev_key, ts in device_last_seen.items() if now - ts > args.timeout}

            if timed_out_devices:
                device_last_seen = {dev_key: ts for dev_key, ts in device_last_seen.items() if dev_key not in timed_out_devices}
                known_endpoints = {
                    ep_key for ep_key in known_endpoints
                    if ep_key.device_key() not in timed_out_devices
                }

            display_stats(args, known_endpoints, traffic_data)
            stats.clear()
    except KeyboardInterrupt:
        print("\nDetaching...")


if __name__ == "__main__":
    main()
