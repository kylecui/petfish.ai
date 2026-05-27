#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""Probe local or remote Linux host readiness and emit JSON."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any


CHECK_COMMANDS = [
    "git", "curl", "jq", "python3", "uv", "node", "npm", "pnpm", "go",
    "java", "mvn", "gradle", "docker", "systemctl", "journalctl",
    "nginx", "kubectl", "helm", "rsync", "ss",
]


def run(cmd: str, ssh_target: str | None = None) -> dict[str, Any]:
    actual = cmd
    if ssh_target:
        actual = f"ssh {shlex.quote(ssh_target)} {shlex.quote(cmd)}"
    proc = subprocess.run(
        actual,
        shell=True,
        text=True,
        capture_output=True,
    )
    return {
        "cmd": actual,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def safe_stdout(cmd: str, ssh_target: str | None = None) -> str:
    return run(cmd, ssh_target)["stdout"]


def which_map(ssh_target: str | None = None) -> dict[str, bool]:
    result = {}
    for name in CHECK_COMMANDS:
        rc = run(f"command -v {shlex.quote(name)} >/dev/null 2>&1", ssh_target)["returncode"]
        result[name] = (rc == 0)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe host readiness for application deployment and emit JSON.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--local", action="store_true", help="Probe current host")
    group.add_argument("--ssh", help="Probe remote host via ssh, e.g. user@server")
    parser.add_argument("--check-path", action="append", default=[], help="Path to test for existence and writability; repeatable")
    parser.add_argument("--check-port", action="append", default=[], help="TCP port to check for listeners; repeatable")
    parser.add_argument("--output", default="-", help="Output file path or - for stdout")
    args = parser.parse_args()

    ssh_target = None if args.local else args.ssh

    os_release = safe_stdout("cat /etc/os-release 2>/dev/null || true", ssh_target)
    uname = safe_stdout("uname -a 2>/dev/null || true", ssh_target)
    hostname = safe_stdout("hostname 2>/dev/null || true", ssh_target)
    cpu = safe_stdout("nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || true", ssh_target)
    mem = safe_stdout("grep -E 'MemTotal|MemAvailable' /proc/meminfo 2>/dev/null || true", ssh_target)
    disk = safe_stdout("df -hP 2>/dev/null || true", ssh_target)
    ip = safe_stdout("hostname -I 2>/dev/null || ip addr 2>/dev/null || true", ssh_target)
    listeners = safe_stdout("ss -ltn 2>/dev/null || true", ssh_target)
    whoami = safe_stdout("whoami 2>/dev/null || true", ssh_target)
    sudo_check = run("sudo -n true >/dev/null 2>&1", ssh_target)["returncode"] == 0

    path_checks = []
    for raw in args.check_path:
        p = shlex.quote(raw)
        exists = run(f"test -e {p}", ssh_target)["returncode"] == 0
        is_dir = run(f"test -d {p}", ssh_target)["returncode"] == 0
        writable = run(f"test -w {p}", ssh_target)["returncode"] == 0
        parent_writable = run(f"test -w $(dirname {p})", ssh_target)["returncode"] == 0
        path_checks.append({
            "path": raw,
            "exists": exists,
            "is_dir": is_dir,
            "writable": writable,
            "parent_writable": parent_writable,
        })

    port_checks = []
    for port in args.check_port:
        cmd = f"ss -ltn '( sport = :{shlex.quote(str(port))} )' 2>/dev/null | tail -n +2"
        out = safe_stdout(cmd, ssh_target)
        port_checks.append({
            "port": str(port),
            "occupied": bool(out.strip()),
            "raw": out.strip(),
        })

    payload = {
        "mode": "local" if args.local else "ssh",
        "target": "localhost" if args.local else args.ssh,
        "summary": {
            "hostname": hostname,
            "whoami": whoami,
            "sudo_nopasswd": sudo_check,
        },
        "system": {
            "uname": uname,
            "os_release": os_release,
            "cpu": cpu,
            "memory": mem,
            "disk": disk,
            "ip": ip,
        },
        "commands": which_map(ssh_target),
        "paths": path_checks,
        "ports": port_checks,
        "listeners": listeners,
        "recommendations": [
            "Confirm runtime/tool availability against repo requirements",
            "Confirm target paths are writable and persistent",
            "Confirm required ports are available or routed through reverse proxy",
            "Confirm service management method: docker, compose, systemd, or k8s",
        ],
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
