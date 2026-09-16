"""Read-only macOS resource guard for the bounded local research run."""
import re
import subprocess
import time

MAX_SWAP_GROWTH_BYTES = 256 * 1024**2
MAX_SWAPOUT_BYTES = 128 * 1024**2
MIN_FREE_PERCENT = 20


def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=10).stdout


def parse_snapshot(sysctl, pressure, vmstat):
    level = re.search(r'kern.memorystatus_vm_pressure_level:\s*(\d+)', sysctl)
    used = re.search(r'used\s*=\s*([\d.]+)([KMG])', sysctl)
    free = re.search(r'System-wide memory free percentage:\s*(\d+)%', pressure)
    page = re.search(r'page size of (\d+) bytes', vmstat)
    outs = re.search(r'Swapouts:\s*(\d+)', vmstat)
    if not all((level, used, free, page, outs)):
        raise ValueError('Incomplete memory telemetry; refusing inference')
    return {'captured_unix': time.time(), 'pressure_level': int(level[1]),
            'free_percent': int(free[1]),
            'swap_used_bytes': int(float(used[1]) * {'K':1024, 'M':1024**2, 'G':1024**3}[used[2]]),
            'swapouts_bytes': int(outs[1]) * int(page[1])}


def snapshot():
    return parse_snapshot(command(['/usr/sbin/sysctl', 'kern.memorystatus_vm_pressure_level', 'vm.swapusage']),
                          command(['/usr/bin/memory_pressure', '-Q']), command(['/usr/bin/vm_stat']))


def violations(current, baseline=None):
    reasons = []
    if current['pressure_level'] != 1:
        reasons.append('memory pressure is not normal')
    if current['free_percent'] < MIN_FREE_PERCENT:
        reasons.append('memory free percentage below 20')
    if baseline:
        if current['swap_used_bytes'] - baseline['swap_used_bytes'] > MAX_SWAP_GROWTH_BYTES:
            reasons.append('swap usage grew by more than 256 MiB')
        if current['swapouts_bytes'] - baseline['swapouts_bytes'] > MAX_SWAPOUT_BYTES:
            reasons.append('more than 128 MiB of additional swapouts')
    return reasons
