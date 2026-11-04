from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager


from app.core.config import settings
from app.core.logger import logger

from app.api.auth import router as auth_router
from app.api.incidents import router as incidents_router
from app.api.investigation import router as investigation_router    
from app.api.evidence import router as evidence_router  
from app.api.action_queue import router as action_queue_router    
from app.api.logs import router as logs_router  
from app.api.monitoring import router as monitoring_router  
from app.api.clients import router as clients_router  
from app.api.servers import router as servers_router  
from app.api.applications import router as applications_router
from app.services.monitoring_scheduler import (
    monitoring_loop,
    coolify_polling_loop,
)
from app.api.metrics import router as metrics_router
from app.api.incident_evidence import router as incident_evidence_router  
from app.api.websocket import router as websocket_router    


@asynccontextmanager
async def lifespan(app):
    from app.services.log_websocket import log_ws_manager

    # Capture main event loop for thread-safe WebSocket broadcasts
    log_ws_manager.set_main_loop(asyncio.get_running_loop())

    monitoring_task = asyncio.create_task(
        monitoring_loop()
    )

    coolify_task = asyncio.create_task(
        coolify_polling_loop()
    )

    print(
        "[MONITORING] "
        "Automatic monitoring enabled."
    )

    try:

        yield

    finally:

        monitoring_task.cancel()
        coolify_task.cancel()

        for task in (monitoring_task, coolify_task):

            try:

                await task

            except asyncio.CancelledError:

                pass

        print(
            "[MONITORING] "
            "Automatic monitoring stopped."
        )


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,prefix="/api")
app.include_router(incidents_router,prefix="/api")
app.include_router(investigation_router,prefix="/api")
app.include_router(evidence_router,prefix="/api")
app.include_router(action_queue_router,prefix="/api")
app.include_router(logs_router,prefix="/api")
app.include_router(monitoring_router,prefix="/api")
app.include_router(clients_router,prefix="/api")
app.include_router(servers_router,prefix="/api")
app.include_router(applications_router,prefix="/api")
app.include_router(metrics_router,prefix="/api")
app.include_router(incident_evidence_router,prefix="/api")
app.include_router(websocket_router,prefix="/api")


@app.on_event("startup")
def startup():
    logger.info("Application Started")


@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {
        "message": f"{settings.APP_NAME} is running."
    }


@app.get("/health")
def health():

    logger.info("Health check executed")

    return {
        "status": "healthy"
    }