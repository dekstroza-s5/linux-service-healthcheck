# Linux Service Healthcheck

Dependency-free Python utility for checking HTTP endpoints, TCP ports, DNS records, TLS certificate expiry and systemd units.

```bash
python3 healthcheck.py --config config.example.json
```

The process exits non-zero when any critical check fails, making it suitable for cron, systemd timers and monitoring agents.
