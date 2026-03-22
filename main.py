from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from utils.monitors import get_all_metrics, get_cpu_load, get_ram_usage, get_uptime

# Lifespan для инициализации
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Ubuntu Core Monitor started")
    yield
    # Shutdown
    print("🛑 Ubuntu Core Monitor stopped")

app = FastAPI(
    title="Ubuntu Core Monitor",
    description="Cyberpunk-style system dashboard",
    lifespan=lifespan
)

# Добавляем CORS для доступа с другого домена
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ismail.soon.it:8443"], # Или ["*"] для теста
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Главная страница с реальными данными"""
    metrics = get_all_metrics()

    context = {
        "request": request,
        # System Info
        "os_name": metrics["system"]["info"]["full_name"],
        # VPN (обновлённый)
        "vpn_protocol": metrics["vpn"]["protocol"],  # "XRay" или "Hysteria"
        "vpn_peers": metrics["vpn"]["peers"],
        "vpn_in": metrics["vpn"]["traffic_in"],
        "vpn_out": metrics["vpn"]["traffic_out"],
        "vpn_load": metrics["vpn"]["load"],
        "vpn_active": metrics["vpn"]["active"],
        "vpn_delay": metrics["vpn"]["delay"],  # Только для XRay
        "vpn_alive": metrics["vpn"]["alive"],  # Только для XRay
        "xray_active": metrics["vpn"]["xray_active"],
        "hysteria_active": metrics["vpn"]["hysteria_active"],
        # Uptime
        "uptime": metrics["system"]["uptime"],
        # Telegram Proxy
        "tg_requests": int(metrics["proxy"]["requests"]),
        "tg_latency": metrics["proxy"]["latency"],
        "proxy_enabled": metrics["proxy"]["enabled"],
        # FastAPI/System
        "api_cpu": metrics["fastapi"]["cpu_load"],
        "api_ram": metrics["fastapi"]["ram_usage"],
        "api_health": metrics["fastapi"]["health"],
        "api_current_uptime": metrics["fastapi"]["current_uptime"],  # Добавляем новое значение
        # Docker
        "docker_active": metrics["docker"]["active"],
        "docker_count": metrics["docker"]["containers"],
        "docker_load": metrics["docker"]["load"],
        # System
        "cpu_load": metrics["system"]["cpu_load"],
        "ram_percent": metrics["system"]["ram"]["percent"],
        "timestamp": metrics["timestamp"]
    }

    return templates.TemplateResponse("dashboard.html", context)

@app.get("/api/v1/status")
async def api_status():
    """JSON API для получения всех метрик"""
    return get_all_metrics()

@app.get("/api/v1/refresh")
async def refresh_metrics():
    """API для обновления данных на фронтенде"""
    metrics = get_all_metrics()
    return {
        "vpn": {
            "protocol": metrics["vpn"]["protocol"],
            "peers": metrics["vpn"]["peers"],
            "in": metrics["vpn"]["traffic_in"],
            "out": metrics["vpn"]["traffic_out"],
            "load": metrics["vpn"]["load"],
            "active": metrics["vpn"]["active"],
            "delay": metrics["vpn"]["delay"],
            "alive": metrics["vpn"]["alive"]
        },
        "uptime": metrics["system"]["uptime"],
        "os_name": metrics["system"]["info"]["full_name"],
        "telegram": {
            "requests": int(metrics["proxy"]["requests"]),
            "latency": metrics["proxy"]["latency"],
            "enabled": metrics["proxy"]["enabled"]
        },
        "fastapi": {
            "uptime": metrics["fastapi"]["current_uptime"],  # Обновляем ключ
            "cpu": metrics["fastapi"]["cpu_load"],
            "ram": metrics["fastapi"]["ram_usage"],
            "health": metrics["fastapi"]["health"]
        },
        "docker": {
            "active": metrics["docker"]["active"],
            "containers": metrics["docker"]["containers"],
            "load": metrics["docker"]["load"]
        },
        "system": {
            "cpu": metrics["system"]["cpu_load"],
            "ram": metrics["system"]["ram"]["percent"]
        },
        "timestamp": metrics["timestamp"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": get_all_metrics()["timestamp"]}

@app.get("/api/v1/docker")
async def docker_info():
    """Детальная информация о Docker"""
    from utils.monitors import check_docker_status
    return check_docker_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)