from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
import httpx
import time
from datetime import datetime
import ssl
import socket
from urllib.parse import urlparse

app = FastAPI(title="Cloud Uptime & API Monitor")

# الخدمات الأساسية
monitored_services = [
    {"id": 1, "name": "Google Cloud", "url": "https://cloud.google.com", "status": "Pending", "latency": 0, "last_checked": "-", "ssl_days": 0, "history": []},
    {"id": 2, "name": "GitHub API", "url": "https://api.github.com", "status": "Pending", "latency": 0, "last_checked": "-", "ssl_days": 0, "history": []}
]

class ServiceCreate(BaseModel):
    name: str
    url: str

def get_ssl_expiry_days(url: str):
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if not hostname:
            return 0
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                not_after = cert.get('notAfter')
                if not_after:
                    expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                    remaining_days = (expiry_date - datetime.utcnow()).days
                    return max(0, remaining_days)
    except Exception:
        return 0
    return 0

def check_services():
    for service in monitored_services:
        start_time = time.time()
        try:
            response = httpx.get(service["url"], timeout=5.0)
            latency = round((time.time() - start_time) * 1000, 2)
            service["status"] = "Online" if response.status_code < 400 else f"Error {response.status_code}"
            service["latency"] = latency
        except Exception:
            service["status"] = "Offline"
            service["latency"] = 0
        
        service["ssl_days"] = get_ssl_expiry_days(service["url"])
        now = datetime.now().strftime("%H:%M:%S")
        service["last_checked"] = now
        service["history"].append({"time": now, "latency": service["latency"]})
        if len(service["history"]) > 10:
            service["history"].pop(0)

scheduler = BackgroundScheduler()
scheduler.add_job(check_services, "interval", seconds=30)
scheduler.start()

@app.on_event("startup")
def startup_event():
    check_services()

@app.get("/api/services")
def get_services():
    return monitored_services

@app.post("/api/services")
def add_service(service: ServiceCreate):
    new_id = len(monitored_services) + 1
    url = service.url if service.url.startswith("http") else f"https://{service.url}"
    new_item = {
        "id": new_id,
        "name": service.name,
        "url": url,
        "status": "Checking...",
        "latency": 0,
        "last_checked": "-",
        "ssl_days": get_ssl_expiry_days(url),
        "history": []
    }
    monitored_services.append(new_item)
    check_services()
    return new_item
