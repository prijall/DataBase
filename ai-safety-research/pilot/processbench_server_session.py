#!/usr/bin/env python3
"""Hold one temporary remote Ollama server; all controller/log files stay local.

Run with --log LOCAL_PATH, then send STOP or close stdin. This does not load a
model, create a tunnel, change launch services, or install anything remotely.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time

HOST = "prabs@100.74.220.25"
REMOTE_CODE = r'''
import hashlib, json, os, selectors, signal, socket, subprocess, sys, time

child = None
stopping = False
reason = "startup_failure"
def event(kind, **fields):
    print("SESSION " + json.dumps(dict(event=kind, **fields)), flush=True)
def stop_signal(signum, frame):
    global stopping, reason
    stopping, reason = True, "signal_" + str(signum)
for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
    signal.signal(sig, stop_signal)
try:
    # Refuse an existing listener. The child owns its own process group; never
    # discover/kill another user's server or runner by name or port.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 11435))
    executable = "/Applications/Ollama.app/Contents/Resources/ollama"
    if not os.access(executable, os.X_OK):
        raise RuntimeError("Existing Ollama executable is unavailable")
    env = dict(os.environ, OLLAMA_HOST="127.0.0.1:11435", OLLAMA_NO_CLOUD="1",
               OLLAMA_NUM_PARALLEL="1", OLLAMA_MAX_LOADED_MODELS="1",
               OLLAMA_NOHISTORY="1", OLLAMA_NOPRUNE="1")
    cache_override = globals().get("CACHE_RAM_MIB")
    if cache_override is not None:
        if type(cache_override) is not int or cache_override != 0:
            raise ValueError("Only explicit cache disable (0) is supported")
        env["LLAMA_ARG_CACHE_RAM"] = "0"
    event("service_environment", cache_ram_override=cache_override,
          allowlisted_environment={key: env[key] for key in ("LLAMA_ARG_CACHE_RAM",) if key in env},
          launcher_source_sha256=globals().get("LAUNCHER_SOURCE_SHA256"))
    if stopping:
        raise RuntimeError("Stopped before server start")
    diagnostic = globals().get("DIAGNOSTIC_SERVICE", False)
    budget_seconds = 600 if diagnostic else 5400
    budget_started = float(sys.argv[1]) if diagnostic and len(sys.argv) == 2 else time.time()
    if diagnostic and not 0 <= time.time() - budget_started < 450:
        raise RuntimeError("Diagnostic service budget invalid or expired")
    child = subprocess.Popen([executable, "serve"], env=env,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    event("spawned", pid=child.pid, pgid=child.pid, watchdog_seconds=budget_seconds,
          readiness="not_yet_checked", budget_started_unix=budget_started)
    # Diagnostic shutdown begins with twelve seconds left for owned cleanup.
    duration = max(0, 600 - (time.time() - budget_started) - 12) if diagnostic else 5400
    deadline = time.monotonic() + duration
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin.fileno(), selectors.EVENT_READ)
    pending = b""
    while not stopping:
        if child.poll() is not None:
            reason = "server_exited"
            break
        if time.monotonic() >= deadline:
            reason = "watchdog"
            break
        if selector.select(timeout=min(1, max(0, deadline-time.monotonic()))):
            data = os.read(sys.stdin.fileno(), 4096)
            if not data:
                reason = "stdin_eof"
                break
            pending += data
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                if line.strip() == b"STOP":
                    stopping, reason = True, "requested_stop"
                    break
                event("ignored_control", reason="expected_STOP")
            if len(pending) > 4096:
                raise RuntimeError("Control line too long")
    selector.close()
finally:
    if child is not None:
        # Also clean descendants if the server itself exited first.
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(child.pid, sig)
            except ProcessLookupError:
                break
            until = time.monotonic() + (8 if sig == signal.SIGTERM else 2)
            while time.monotonic() < until:
                child.poll()  # Reap the group leader if it has exited.
                try:
                    os.killpg(child.pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.1)
            else:
                continue
            break
        try:
            child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(child.pid, 0)
            group_absent = False
        except ProcessLookupError:
            group_absent = True
        # This event may fail on disconnected SSH, after cleanup has run.
        event("cleanup", pid=child.pid, reason=reason, returncode=child.returncode,
              owned_group_absent=group_absent)
        if not group_absent:
            raise RuntimeError("Owned process group still present after cleanup")
'''


def remote_code(cache_ram_mib=None):
    if cache_ram_mib is not None and (type(cache_ram_mib) is not int or cache_ram_mib != 0):
        raise ValueError("Only cache-ram-mib 0 is supported")
    if cache_ram_mib is None:
        return REMOTE_CODE
    prefix = "CACHE_RAM_MIB = 0\nDIAGNOSTIC_SERVICE = True\nLAUNCHER_SOURCE_SHA256 = " + repr(hashlib.sha256(REMOTE_CODE.encode()).hexdigest()) + "\n"
    return prefix + REMOTE_CODE


def ssh_command(cache_ram_mib=None, budget_started=None):
    remote = "python3 -B -c " + shlex.quote(remote_code(cache_ram_mib))
    if cache_ram_mib == 0 and budget_started is not None:
        remote += " " + shlex.quote(str(float(budget_started)))
    return ["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
            "-o", "ControlMaster=no", "-o", "ControlPath=none",
            "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=10",
            "-o", "ServerAliveCountMax=3", HOST, remote]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True, help="New local log file")
    parser.add_argument("--cache-ram-mib", type=int, choices=(0,), default=None,
                        help="Explicitly disable backend prompt-state RAM cache for this owned service")
    args = parser.parse_args()
    def interrupted(signum, frame):
        raise KeyboardInterrupt
    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, interrupted)
    # Exclusive creation preserves prior evidence; input stays attached to SSH.
    with args.log.open("xb") as log:
        started = time.time()
        header = {"event": "local_start", "host": HOST, "budget_started_unix": started,
                  "remote_code_sha256": hashlib.sha256(remote_code(args.cache_ram_mib).encode()).hexdigest(),
                  "cache_ram_mib": args.cache_ram_mib,
                  "launcher_file_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        log.write((json.dumps(header) + "\n").encode())
        log.flush()
        process = subprocess.Popen(ssh_command(args.cache_ram_mib, started), stdin=sys.stdin,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            while chunk := process.stdout.read1(65536):
                log.write(chunk)
                log.flush()
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
            return process.wait()
        finally:
            if process.poll() is None:
                # SSH teardown closes remote stdin / delivers HUP. The remote
                # finally block owns server cleanup; watchdog also bounds life.
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            log.write((json.dumps({"event": "local_end",
                                   "ssh_returncode": process.returncode}) + "\n").encode())
            log.flush()


if __name__ == "__main__":
    raise SystemExit(main())
