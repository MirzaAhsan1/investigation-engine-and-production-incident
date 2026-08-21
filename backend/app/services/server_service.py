from uuid import UUID

from sqlalchemy.orm import Session

from app.models.server import Server
from app.models.system_metric import SystemMetric
from app.models.incident import Incident
from app.models.application import Application
from app.models.enums import StatusEnum


def create_server(
    db: Session,
    payload,
):
    server = Server(
        client_id=payload.client_id,
        name=payload.name,
        host=payload.host,
        environment=payload.environment,
    )

    db.add(server)
    db.commit()
    db.refresh(server)

    return server


def get_servers(
    db: Session,
):
    return (
        db.query(Server)
        .order_by(Server.name)
        .all()
    )


def get_server(
    db: Session,
    server_id: UUID,
):
    return db.get(
        Server,
        server_id,
    )


def get_servers_by_client(
    db: Session,
    client_id: UUID,
):
    return (
        db.query(Server)
        .filter(
            Server.client_id == client_id,
            Server.is_active == True,
        )
        .all()
    )


def get_server_by_host(
    db: Session,
    client_id: UUID,
    host: str,
):
    return (
        db.query(Server)
        .filter(
            Server.client_id == client_id,
            Server.host == host,
            Server.is_active == True,
        )
        .first()
    )


def get_servers_stats(
    db: Session,
    limit: int = 50,
):
    """
    Get aggregated real-time metrics stats per server:
    cpu_usage, memory_usage, disk_usage, latest error_rate, open incident count per server.

    Picks the LATEST NON-NULL value per metric field across recent metric rows for each server
    (handling case where Fluent Bit sends CPU, Memory, and Disk in separate metrics rows).
    """
    servers = (
        db.query(Server)
        .filter(Server.is_active == True)
        .all()
    )

    stats = []
    for server in servers:
        # Fetch recent metric rows for this server (newest first)
        recent_metrics = (
            db.query(SystemMetric)
            .filter(SystemMetric.server_id == server.id)
            .order_by(SystemMetric.timestamp.desc())
            .limit(limit)
            .all()
        )

        # Coalesce latest non-null value for each metric field
        cpu_usage = None
        memory_usage = None
        disk_usage = None
        http_5xx_count = None
        request_count = None
        latest_timestamp = None

        for m in recent_metrics:
            if latest_timestamp is None and m.timestamp is not None:
                latest_timestamp = m.timestamp
            if cpu_usage is None and m.cpu_usage is not None:
                cpu_usage = m.cpu_usage
            if memory_usage is None and m.memory_usage is not None:
                memory_usage = m.memory_usage
            if disk_usage is None and m.disk_usage is not None:
                disk_usage = m.disk_usage
            if http_5xx_count is None and m.http_5xx_count is not None:
                http_5xx_count = m.http_5xx_count
            if request_count is None and m.request_count is not None:
                request_count = m.request_count

        # Count open incidents associated with applications on this server
        open_incidents_count = (
            db.query(Incident)
            .join(Application, Incident.application_id == Application.id)
            .filter(
                Application.server_id == server.id,
                Incident.status == StatusEnum.OPEN,
            )
            .count()
        )

        # Calculate error_rate with division-by-zero guard
        error_rate = 0.0
        if (
            http_5xx_count is not None
            and request_count is not None
            and request_count > 0
        ):
            error_rate = round(http_5xx_count / request_count, 4)

        stats.append({
            "server_id": str(server.id),
            "name": server.name,
            "host": server.host,
            "environment": server.environment,
            "cpu_usage": cpu_usage if cpu_usage is not None else 0.0,
            "memory_usage": memory_usage if memory_usage is not None else 0.0,
            "disk_usage": disk_usage if disk_usage is not None else 0.0,
            "error_rate": error_rate,
            "open_incidents_count": open_incidents_count,
            "timestamp": latest_timestamp.isoformat() if latest_timestamp else None,
        })

    return stats