from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import logger
from app.api.routes_logs import router as logs_router
from app.api.routes_alerts import router as alerts_router
from app.api.routes_stats import router as stats_router
from app.auth.signup import router as auth_router
from app.auth.login import router as login_router
from app.auth.admin_routes import router as admin_router
from app.api.threats import router as threats_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://net-guard-viz.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(stats_router)
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(login_router, prefix="/auth", tags=["Auth"])
app.include_router(admin_router)
app.include_router(threats_router, prefix="/api/threats", tags=["Threats"])

@app.get("/")
def read_root():
    return {"message": "NetGuardViz Running"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response