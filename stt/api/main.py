import structlog
from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from stt.api import V1_PREFIX
from stt.api.v1.router import v_router as v1_router
from stt.db.database import close_clean_up_pooled_connections, create_db_and_tables
from stt.exceptions import BaseInternalError, ExceptionModel, RichHTTPException

logger = structlog.get_logger(__file__)
app = FastAPI()


origins = [
    f"{protocol}://{domain}:3000"
    for protocol in ("http", "https")
    for domain in ("localhost", "0.0.0.0", "127.0.0.1")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def base_internal_error_handler(request: Request, exc: Exception):
    """Handler for BaseInternalError exceptions"""
    return_exc = RichHTTPException(
        status_code=500,
        model=ExceptionModel(
            description="Could not process request. Please try again later.",
            hint=exc.message
            if isinstance(exc, BaseInternalError)
            else f"{str(type(exc))}, {exc.args}",
        ),
    )
    return await http_exception_handler(request, return_exc)


@app.get("/status")
async def get_status():
    return {"status": "OK"}


#
# Special events
#
@app.on_event("startup")
async def startup():
    # Not needed if Alembic
    await logger.ainfo("Starting up...")
    await create_db_and_tables()


@app.on_event("shutdown")
async def shutdown():
    await logger.ainfo("Shutting down...")
    await close_clean_up_pooled_connections()


#
# API
#
app.include_router(v1_router, prefix=V1_PREFIX)
