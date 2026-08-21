from uuid import uuid4
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.server import Server
from app.models.application import Application
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.action_queue import ActionQueue
from app.models.system_metric import SystemMetric
from app.models.enums import SeverityEnum, StatusEnum, IncidentTypeEnum, IncidentSourceEnum
from app.enums.action_status import ActionStatusEnum

from app.services.incident_service import get_all_incidents, create_incident_from_group, get_or_create_system_user
from app.services.action_queue_service import update_action_status, get_actions_by_incident
from app.services.server_service import get_servers_stats


def test_get_all_incidents_includes_investigation(db_session: Session):
    user = get_or_create_system_user(db_session)
    
    # Create incident
    incident = Incident(
        title="Test Gateway Latency",
        description="High latency on API gateway",
        incident_type=IncidentTypeEnum.APPLICATION,
        severity=SeverityEnum.HIGH,
        status=StatusEnum.OPEN,
        source=IncidentSourceEnum.MONITORING,
        reported_by=user.id,
    )
    db_session.add(incident)
    db_session.flush()

    # Create investigation linked to incident
    investigation = Investigation(
        incident_id=incident.id,
        predicted_category="Network / Latency",
        predicted_cause="Upstream Service Timeout",
        confidence=92.5,
        risk_score=75.0,
        root_cause="Database pool exhausted in payment worker",
        reasoning="Spike in 5xx errors matched DB timeout pattern",
        recommended_actions="Scale worker pool",
    )
    db_session.add(investigation)
    db_session.commit()

    incidents = get_all_incidents(db_session)
    assert len(incidents) >= 1
    target = next((i for i in incidents if i.id == incident.id), None)
    assert target is not None
    assert target.investigation is not None
    assert target.investigation.predicted_category == "Network / Latency"
    assert target.investigation.root_cause == "Database pool exhausted in payment worker"


def test_update_action_status_approves_and_denies(db_session: Session):
    user = get_or_create_system_user(db_session)
    incident = Incident(
        title="Action Test Incident",
        description="Testing action queue status updates",
        incident_type=IncidentTypeEnum.APPLICATION,
        severity=SeverityEnum.MEDIUM,
        status=StatusEnum.OPEN,
        source=IncidentSourceEnum.MONITORING,
        reported_by=user.id,
    )
    db_session.add(incident)
    db_session.flush()

    investigation = Investigation(
        incident_id=incident.id,
        predicted_category="Memory",
        predicted_cause="Memory Leak",
        confidence=88.0,
        risk_score=60.0,
    )
    db_session.add(investigation)
    db_session.flush()

    action = ActionQueue(
        investigation_id=investigation.id,
        title="Restart container payment-worker",
        action_type="RESTART_CONTAINER",
        target="payment-worker",
        priority=1,
        confidence=90.0,
        status=ActionStatusEnum.PENDING_APPROVAL,
    )
    db_session.add(action)
    db_session.commit()

    # Approve
    updated = update_action_status(db_session, action, ActionStatusEnum.APPROVED, approved_by=user.id)
    assert updated.status == ActionStatusEnum.APPROVED
    assert updated.approved_by == user.id

    # Deny / Reject
    rejected = update_action_status(db_session, action, ActionStatusEnum.REJECTED, approved_by=user.id)
    assert rejected.status == ActionStatusEnum.REJECTED

    # Test actions by incident retrieval
    actions_list = get_actions_by_incident(db_session, incident.id)
    assert len(actions_list) == 1
    assert actions_list[0].id == action.id


def test_get_servers_stats(db_session: Session):
    client = Client(name="Test Client", api_key=str(uuid4()))
    db_session.add(client)
    db_session.flush()

    server = Server(
        client_id=client.id,
        name="prod-server-test-01",
        host="10.0.0.99",
        environment="production",
        is_active=True,
    )
    db_session.add(server)
    db_session.flush()

    metric = SystemMetric(
        client_id=client.id,
        server_id=server.id,
        cpu_usage=64.5,
        memory_usage=81.2,
        disk_usage=45.0,
        http_5xx_count=4,
        request_count=100,
        timestamp=datetime.now(timezone.utc),
    )
    db_session.add(metric)
    db_session.commit()

    stats = get_servers_stats(db_session)
    assert len(stats) >= 1
    target = next((s for s in stats if s["server_id"] == str(server.id)), None)
    assert target is not None
    assert target["cpu_usage"] == 64.5
    assert target["memory_usage"] == 81.2
    assert target["error_rate"] == 0.04
