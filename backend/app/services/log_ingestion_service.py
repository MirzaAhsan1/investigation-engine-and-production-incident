from sqlalchemy.orm import Session

from app.monitoring.log_filter import is_interesting_log
from app.monitoring.log_fingerprint import generate_log_fingerprint
from app.monitoring.log_level import classify_log_level
from app.schemas.log_ingest import LogIngestRequest

from app.services.client_service import get_client_by_api_key

from app.services.log_storage_service import (
    get_log_by_fingerprint,
    update_duplicate_log,
    save_log,
)

from app.services.correlation_service import correlate_log

from app.services.server_service import (
    get_server_by_host,
    create_server,
)

from app.services.application_service import (
    get_application_by_container,
    create_application,
)


def ingest_log_batch(
    db: Session,
    logs: list[LogIngestRequest],
):
    """
    Ingestion pipeline (sync).

    Flow:

        LogEvent
            ↓
        CorrelationGroup

    IMPORTANT:

    Evidence / Incident / ML Prediction / LLM Investigation
    are NOT done here. They are owned exclusively by the
    async monitoring worker:

        monitoring_worker.process_pending_logs()
            -> monitoring_service.process_log()
            -> investigation_pipeline.start_investigation()

    This endpoint only ingests, correlates, and leaves the
    log's status as PENDING so the worker picks it up and
    runs the full evidence -> incident -> ML -> LLM ->
    investigation flow exactly once.
    """

    if not logs:
        return []

    try:

        # =====================================================
        # 1. Authorize Client
        # =====================================================

        api_key = logs[0].api_key

        client = get_client_by_api_key(
            db=db,
            api_key=api_key,
        )

        if client is None:

            db.rollback()

            return [
                {
                    "status": "unauthorized",
                    "reason": "Invalid monitoring API key",
                }
            ]

        # =====================================================
        # Caches
        # =====================================================

        server_cache = {}
        app_cache = {}

        results = []

        ws_payloads = []

        # =====================================================
        # 2. Process Every Log
        # =====================================================

        for log in logs:

            # =================================================
            # 2A. Resolve Server
            # =================================================

            if log.host not in server_cache:

                server = get_server_by_host(
                    db=db,
                    client_id=client.id,
                    host=log.host,
                )

                if server is None:

                    class ServerPayload:

                        client_id = client.id
                        name = log.host
                        host = log.host
                        environment = "production"

                    server = create_server(
                        db=db,
                        payload=ServerPayload(),
                    )

                server_cache[
                    log.host
                ] = server

            else:

                server = server_cache[
                    log.host
                ]

            # =================================================
            # 2B. Resolve Application / Container
            # =================================================

            app_key = (
                f"{server.id}:{log.container_name}"
            )

            if app_key not in app_cache:

                application = (
                    get_application_by_container(
                        db=db,
                        server_id=server.id,
                        container_name=log.container_name,
                    )
                )

                if application is None:

                    class ApplicationPayload:

                        server_id = server.id
                        name = log.container_name
                        container_name = log.container_name
                        provider = "coolify"
                        resource_uuid = None

                    application = create_application(
                        db=db,
                        payload=ApplicationPayload(),
                    )

                app_cache[
                    app_key
                ] = application

            else:

                application = app_cache[
                    app_key
                ]

            # =================================================
            # 2C. Determine Log Level
            # =================================================

            level = (
                log.level
                or classify_log_level(
                    log.message
                )
            )

            # =================================================
            # 2D. WebSocket Payload
            # =================================================

            ws_payloads.append(
                {
                    "timestamp": (
                        log.timestamp.isoformat()
                        if hasattr(
                            log.timestamp,
                            "isoformat",
                        )
                        else str(
                            log.timestamp
                        )
                    ),
                    "level": level,
                    "message": (
                        log.message[:1000]
                        if log.message
                        else log.message
                    ),
                    "container_name": (
                        log.container_name
                    ),
                    "host": log.host,
                }
            )

            # =================================================
            # 2E. Interesting Log Check
            # =================================================

            interesting, reason = (
                is_interesting_log(
                    level=level,
                    message=log.message,
                )
            )

            if not interesting:

                results.append(
                    {
                        "status": "ignored",
                        "reason": reason,
                    }
                )

                continue

            # =================================================
            # 3. Fingerprint
            # =================================================

            fingerprint = (
                generate_log_fingerprint(
                    client_id=client.id,
                    server_id=server.id,
                    application_id=application.id,
                    level=level,
                    message=log.message,
                )
            )

            # =================================================
            # 4. Check Duplicate
            # =================================================

            existing_log = (
                get_log_by_fingerprint(
                    db=db,
                    client_id=client.id,
                    server_id=server.id,
                    application_id=application.id,
                    fingerprint=fingerprint,
                    current_timestamp=log.timestamp,
                )
            )

            if existing_log is not None:

                updated_log = (
                    update_duplicate_log(
                        db=db,
                        existing_log=existing_log,
                        timestamp=log.timestamp,
                    )
                )

                results.append(
                    {
                        "status": "duplicate",
                        "reason": (
                            "Same event detected "
                            "within deduplication window"
                        ),
                        "log_id": str(
                            updated_log.id
                        ),
                        "fingerprint": (
                            updated_log.fingerprint
                        ),
                        "occurrence_count": (
                            updated_log.occurrence_count
                        ),
                        "first_seen": (
                            updated_log.first_seen
                        ),
                        "last_seen": (
                            updated_log.last_seen
                        ),
                        "investigation_triggered": False,
                    }
                )

                continue

            # =================================================
            # 5. Save LogEvent
            # =================================================

            saved = save_log(
                db=db,
                client_id=client.id,
                server_id=server.id,
                application_id=application.id,
                level=level,
                message=log.message,
                timestamp=log.timestamp,
                fingerprint=fingerprint,
            )

            # =================================================
            # 6. Correlation
            # =================================================

            group = correlate_log(
                db=db,
                log=saved,
            )

            if group is None:

                results.append(
                    {
                        "status": "error",
                        "reason": (
                            "Correlation group "
                            "could not be created"
                        ),
                        "log_id": str(
                            saved.id
                        ),
                    }
                )

                continue

            # =================================================
            # 7. Done here.
            #
            # Evidence / Incident / ML / Investigation are
            # owned EXCLUSIVELY by the async monitoring worker.
            # The log's status stays PENDING (set in save_log)
            # so process_pending_logs() picks it up and runs
            # the full pipeline exactly once.
            # =================================================

            results.append(
                {
                    "status": "interesting",
                    "reason": reason,
                    "log_id": str(saved.id),
                    "client_id": str(saved.client_id),
                    "server_id": str(saved.server_id),
                    "application_id": str(saved.application_id),
                    "correlation_group_id": str(group.id),
                    "fingerprint": saved.fingerprint,
                    "occurrence_count": saved.occurrence_count,
                    "first_seen": saved.first_seen,
                    "last_seen": saved.last_seen,
                    "investigation_triggered": False,
                    "investigation_required": True,
                }
            )

        # =====================================================
        # 8. Commit
        # =====================================================

        db.commit()

        # =====================================================
        # 9. WebSocket Broadcast
        # =====================================================

        if ws_payloads:

            try:

                from app.services.log_websocket import (
                    log_ws_manager,
                )

                log_ws_manager.broadcast_sync(
                    ws_payloads
                )

            except Exception as ws_err:

                print(
                    "[WebSocket Stream Warning] "
                    f"Broadcast failed: {ws_err}"
                )

        return results

    except Exception:

        db.rollback()

        raise