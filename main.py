from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
import httpx
import time
from datetime import datetime, timezone
import ssl
import socket
from urllib.parse import urlparse

app = FastAPI(title="Cloud Uptime & API Monitor")

# 3 مواقع افتراضية مضافة مسبقاً لتعمل وتظهر في الجدول والرسم البياني فور فتح الصفحة
monitored_services = [
    {
        "id": 1,
        "name": "Google Search",
        "url": "https://google.com",
        "status": "Online",
        "latency": 120,
        "last_checked": "الآن",
        "ssl_days": 85,
        "history": [
            {"time": "00:01", "latency": 115},
            {"time": "00:02", "latency": 130},
            {"time": "00:03", "latency": 120}
        ]
    },
    {
        "id": 2,
        "name": "GitHub API",
        "url": "https://github.com",
        "status": "Online",
        "latency": 185,
        "last_checked": "الآن",
        "ssl_days": 140,
        "history": [
            {"time": "00:01", "latency": 190},
            {"time": "00:02", "latency": 175},
            {"time": "00:03", "latency": 185}
        ]
    },
    {
        "id": 3,
        "name": "Cloudflare DNS",
        "url": "https://1.1.1",
        "status": "Online",
        "latency": 45,
        "last_checked": "الآن",
        "ssl_days": 210,
        "history": [
            {"time": "00:01", "latency": 48},
            {"time": "00:02", "latency": 42},
            {"time": "00:03", "latency": 45}
        ]
    }
]

class ServiceCreate(BaseModel):
    name: str
    url: str

def get_ssl_expiry_days(url: str):
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if not hostname or parsed_url.scheme != "https":
            return 0
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                not_after = cert.get('notAfter')
                if not_after:
                    expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
                    remaining_days = (expiry_date - datetime.now(timezone.utc)).days
                    return max(0, remaining_days)
    except Exception:
        return 0
    return 0

def check_single_service(service: dict):
    start_time = time.time()
    try:
        response = httpx.get(service["url"], timeout=5.0, follow_redirects=True)
        latency = round((time.time() - start_time) * 1000, 2)
        service["status"] = "Online" if response.status_code < 400 else f"Error {response.status_code}"
        service["latency"] = latency
    except Exception:
        service["status"] = "Offline"
        service["latency"] = 0
    
    ssl_days = get_ssl_expiry_days(service["url"])
    if ssl_days > 0:
        service["ssl_days"] = ssl_days
        
    now = datetime.now().strftime("%H:%M:%S")
    service["last_checked"] = now
    service["history"].append({"time": now, "latency": service["latency"]})
    if len(service["history"]) > 12:
        service["history"].pop(0)

def check_services():
    for service in monitored_services:
        check_single_service(service)

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
    new_id = max([s["id"] for s in monitored_services], default=0) + 1
    url = service.url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
        
    new_item = {
        "id": new_id,
        "name": service.name.strip(),
        "url": url,
        "status": "Checking...",
        "latency": 0,
        "last_checked": "-",
        "ssl_days": 0,
        "history": []
    }
    monitored_services.append(new_item)
    check_single_service(new_item)
    return new_item

@app.delete("/api/services/{service_id}")
def delete_service(service_id: int):
    global monitored_services
    initial_len = len(monitored_services)
    monitored_services = [s for s in monitored_services if s["id"] != service_id]
    if len(monitored_services) == initial_len:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<h1>Index.html not found</h1>"
