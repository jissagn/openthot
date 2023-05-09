import structlog
from fastapi import FastAPI

from stt.api.v1.router import v_router as v1_router
from stt.db.database import close_clean_up_pooled_connections, create_db_and_tables

logger = structlog.get_logger(__file__)
app = FastAPI()


@app.get("/status")
async def get_status():
    return {"status": "OK"}


app.include_router(v1_router, prefix="/api/v1")


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
