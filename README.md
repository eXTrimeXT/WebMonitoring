# Web App on Server

### Info
- URL: http://89.125.87.234:8000/
- using port: 8000
- protocol: http
- lang: python3 (py (see alias))
- time auto update: 10 seconds


### Check Service
```systemctl status server-monitor```

path service: /etc/systemd/system/server-monitor.service
```
[Unit]
Description=Server Health Monitor
After=network.target

[Service]
User=root
WorkingDirectory=/root/webMonitoring
ExecStart=/root/webMonitoring/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

```