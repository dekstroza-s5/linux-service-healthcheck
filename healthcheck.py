#!/usr/bin/env python3
import argparse, json, socket, ssl, subprocess, sys, urllib.request
from datetime import datetime, timezone

def check(item):
    kind, target = item["type"], item["target"]
    timeout = item.get("timeout", 5)
    if kind == "http":
        with urllib.request.urlopen(target, timeout=timeout) as response:
            return 200 <= response.status < 400, f"HTTP {response.status}"
    if kind == "tcp":
        host, port = target.rsplit(":", 1)
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True, "connection successful"
    if kind == "dns":
        return bool(socket.getaddrinfo(target, None)), "record resolved"
    if kind == "systemd":
        result = subprocess.run(["systemctl", "is-active", "--quiet", target], check=False)
        return result.returncode == 0, "active" if result.returncode == 0 else "inactive"
    if kind == "tls":
        host, port = (target.split(":") + ["443"])[:2]
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=host) as sock:
            sock.settimeout(timeout); sock.connect((host, int(port)))
            expires = datetime.fromisoformat(sock.getpeercert()["notAfter"].replace(" GMT", "+00:00"))
            days = (expires - datetime.now(timezone.utc)).days
            return days >= item.get("minimum_days", 14), f"{days} days remaining"
    raise ValueError(f"unsupported check type: {kind}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    checks = json.load(open(args.config, encoding="utf-8"))["checks"]
    failed = 0
    for item in checks:
        try: ok, message = check(item)
        except Exception as exc: ok, message = False, str(exc)
        print(f"{'OK' if ok else 'FAIL'} {item['name']}: {message}")
        failed += not ok
    return 1 if failed else 0

if __name__ == "__main__": sys.exit(main())
