from fastapi import FastAPI, Request
from app.api.routes_logs import router as logs_router
from app.api.routes_alerts import router as alerts_router
from app.api.routes_stats import router as stats_router
from app.auth.signup import router as auth_router
from app.auth.login import router as login_router
from app.auth.admin_routes import router as admin_router
from app.core.logger import logger
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(stats_router)
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(login_router, prefix="/auth", tags=["Auth"])
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.middleware("http")
async def log_requests(request: Request, call_next):

    logger.info(f"{request.method} {request.url}")

    response = await call_next(request)

    return response