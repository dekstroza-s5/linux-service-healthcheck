# Linux Service Healthcheck

Dependency-free Python utility for checking HTTP endpoints, TCP ports, DNS records, TLS certificate expiry and systemd units.

## Supported checks

| Type | Example | Success condition |
|---|---|---|
| HTTP | `https://example.com` | status 200-399 |
| TCP | `127.0.0.1:5432` | connection opens |
| DNS | `example.com` | address resolves |
| TLS | `example.com:443` | certificate has enough days |
| systemd | `nginx` | unit is active |

## Run

```bash
python3 healthcheck.py --config config.example.json
echo $?
```

Example output:

```text
OK website: HTTP 200
OK public DNS: record resolved
FAIL nginx service: inactive
OK certificate: 63 days remaining
```

Exit code is zero only when all checks pass, allowing use by cron, systemd, CI or a monitoring agent.

## Configure

Copy the example and define environment-specific targets. Keep internal names and sensitive endpoints in an untracked configuration file.

## Install with systemd

```bash
sudo useradd --system --home /nonexistent --shell /usr/sbin/nologin monitoring
sudo install -d /opt/service-healthcheck /etc/service-healthcheck
sudo install -m 0755 healthcheck.py /opt/service-healthcheck/
sudo install -m 0644 config.example.json /etc/service-healthcheck/config.json
sudo install -m 0644 systemd/* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now service-healthcheck.timer
systemctl list-timers service-healthcheck.timer
journalctl -u service-healthcheck.service
```

## Troubleshooting

- timeout: test routing, firewall and proxy behavior;
- TLS failure: confirm SNI hostname and system CA bundle;
- systemd check denied: run under a user permitted to inspect units;
- DNS differs from applications: compare resolver configuration and container namespaces.

This tool checks symptoms; production alerting should also include deduplication, routing and recovery notifications.
