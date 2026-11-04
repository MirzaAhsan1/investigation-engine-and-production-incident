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
from app.services.incident_service import create_incident_from_group
# from app.services.investigation_pipeline import start_investigation
from app.services.ml_service import predict_incident
from app.models.evidence import Evidence
from app.services.server_service import get_server_by_host, create_server
from app.services.application_service import (
    get_application_by_container,
    create_application,
)
# from app.services.websocket_manager import websocket_manager
from app.services.evidence_aggregation_service import (
    create_evidence_from_group,
)


def ingest_log_batch(db: Session, logs: list[LogIngestRequest]):
    """
    Optimized batch ingestion service.
    Fixes Joblib/ML crash by executing investigation triggers AFTER db.commit().
    WebSocket broadcast is now batched (one event loop per request, not per log).
    """
    if not logs:
        return []

    try:
        # 1. Authorize Client once per batch
        api_key = logs[0].api_key
        client = get_client_by_api_key(db=db, api_key=api_key)

        if client is None:
            db.rollback()
            return [{"status": "unauthorized", "reason": "Invalid monitoring API key"}]

        server_cache = {}
        app_cache = {}
        results = []
        pending_investigations = []  # Store incident IDs to trigger ML after DB Commit
        ws_payloads = []  # Collect all websocket payloads, broadcast once at the end

        for log in logs:
            # 2. Server Resolution with Caching
            if log.host not in server_cache:
                server = get_server_by_host(db=db, client_id=client.id, host=log.host)
                if server is None:
                    class ServerPayload:
                        client_id = client.id
                        name = log.host
                        host = log.host
                        environment = "production"

                    server = create_server(db=db, payload=ServerPayload())
                server_cache[log.host] = server
            else:
                server = server_cache[log.host]

            # 3. Application Resolution with Caching
            app_key = f"{server.id}:{log.container_name}"
            if app_key not in app_cache:
                application = get_application_by_container(
                    db=db,
                    server_id=server.id,
                    container_name=log.container_name,
                )
                if application is None:
                    class ApplicationPayload:
                        server_id = server.id
                        name = log.container_name
                        container_name = log.container_name
                        provider = "coolify"
                        resource_uuid = None

                    application = create_application(db=db, payload=ApplicationPayload())
                app_cache[app_key] = application
            else:
                application = app_cache[app_key]

            # 4. Level & Filter
            level = log.level or classify_log_level(log.message)

            # Collect payload for WebSocket live stream (broadcast happens once, after the loop)
            ws_payloads.append({
                "timestamp": log.timestamp.isoformat() if hasattr(log.timestamp, "isoformat") else str(log.timestamp),
                "level": level,
                "message": log.message[:1000] if log.message else log.message,
                "container_name": log.container_name,
                "host": log.host,
            })

            interesting, reason = is_interesting_log(level=level, message=log.message)

            if not interesting:
                results.append({"status": "ignored", "reason": reason})
                continue

            # 5. Fingerprint & Deduplication
            fingerprint = generate_log_fingerprint(
                client_id=client.id,
                server_id=server.id,
                application_id=application.id,
                level=level,
                message=log.message,
            )

            existing_log = get_log_by_fingerprint(
                db=db,
                client_id=client.id,
                server_id=server.id,
                application_id=application.id,
                fingerprint=fingerprint,
                current_timestamp=log.timestamp,
            )

            if existing_log is not None:
                updated_log = update_duplicate_log(
                    db=db,
                    existing_log=existing_log,
                    timestamp=log.timestamp,
                )
                results.append({
                    "status": "duplicate",
                    "reason": "Same event detected within deduplication window",
                    "log_id": str(updated_log.id),
                    "fingerprint": updated_log.fingerprint,
                    "occurrence_count": updated_log.occurrence_count,
                    "first_seen": updated_log.first_seen,
                    "last_seen": updated_log.last_seen,
                    "investigation_triggered": False,
                })
                continue

            # 6. Save, Correlate & Incident
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

            group = correlate_log(db=db, log=saved)
            incident = create_incident_from_group(db=db, group=group) if group else None

            # Result metadata layout
            res_item = {
                "status": "interesting",
                "reason": reason,
                "log_id": str(saved.id),
                "client_id": str(saved.client_id),
                "server_id": str(saved.server_id),
                "application_id": str(saved.application_id),
                "correlation_group_id": str(group.id) if group else None,
                "incident_id": str(incident.id) if incident else None,
                "fingerprint": saved.fingerprint,
                "occurrence_count": saved.occurrence_count,
                "first_seen": saved.first_seen,
                "last_seen": saved.last_seen,
                "investigation_triggered": False,
                "investigation_required": incident is not None,
            }

            if incident:
                pending_investigations.append((res_item, incident.id))

            results.append(res_item)

        # ==========================================================
        # 7. COMMIT Database Transactions First (Bug 1 & 2 Fix)
        # Guarantees all LogEvents, CorrelationGroups, Incidents, and Evidence
        # are explicitly committed to the database.
        # ==========================================================
        db.commit()

        # ==========================================================
        # 8. Thread-Safe Broadcast over WebSocket (Bug 3 Fix)
        # Uses thread-safe broadcast bridge to schedule coroutine on main loop.
        # ==========================================================
        if ws_payloads:
            try:
                from app.services.log_websocket import log_ws_manager
                log_ws_manager.broadcast_sync(ws_payloads)
            except Exception as ws_err:
                print(f"[WebSocket Stream Warning] Broadcast failed: {ws_err}")

        # ==========================================================
        # 9. ML Prediction ONLY (Bug 2 Fix - Evidence now committed)
        # ==========================================================

        for res_item, inc_id in pending_investigations:
            try:
                # Get evidence for this incident (now guaranteed committed in DB)
                evidence = (
                    db.query(Evidence)
                    .filter(
                        Evidence.incident_id == inc_id
                    )
                    .first()
                )

                if evidence is None:
                    print(
                        f"[ML] No evidence found for incident {inc_id}"
                    )
                    continue

                # Run ML prediction ONLY
                prediction = predict_incident(db=db, incident_id=incident.id)

                # Add prediction to current response
                res_item["ml_prediction"] = prediction

                print(
                    f"[ML] Prediction completed for incident {inc_id}: "
                    f"{prediction}"
                )

            except Exception as ml_err:
                print(
                    f"[ML ERROR] Prediction failed for incident "
                    f"{inc_id}: {ml_err}"
                )

                res_item["ml_prediction"] = None

        return results

    except Exception:
        db.rollback()
        raise