from __future__ import annotations
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .database import init_db
from .api import auth_router,chat_router,matrix_router,health_router,admin_router,history_router
from .services.matrix_service import bootstrap_existing_matrix
from .services.settings_service import load_runtime_settings
from .rate_limit import enforce_rate_limit

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s %(message)s")
app=FastAPI(title=settings.app_name,version="1.0.0",docs_url="/docs" if settings.app_env!="production" else None,redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def security_headers(request:Request,call_next):
    if request.headers.get("content-length") and int(request.headers["content-length"]) > settings.max_upload_mb*1024*1024 + 1024*1024:
        return JSONResponse(status_code=413,content={"detail":"Request too large."})
    try:
        enforce_rate_limit(request)
    except Exception as exc:
        if getattr(exc,"status_code",None)==429:
            return JSONResponse(status_code=429,content={"detail":"Too many requests. Please try again later."})
        raise
    response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["Referrer-Policy"]="no-referrer"
    response.headers["Permissions-Policy"]="camera=(), microphone=(), geolocation=()"
    response.headers["X-Frame-Options"]="DENY"
    return response

@app.exception_handler(Exception)
async def unhandled(request:Request,exc:Exception):
    logging.exception("Unhandled backend error")
    return JSONResponse(status_code=500,content={"detail":"Unable to process this request."})

@app.on_event("startup")
def startup():
    init_db(); load_runtime_settings(); bootstrap_existing_matrix()

for r in [auth_router,chat_router,matrix_router,health_router,admin_router,history_router]: app.include_router(r,prefix=settings.api_prefix)
