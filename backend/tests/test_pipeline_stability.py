import uuid
from types import SimpleNamespace

from app.enums.action_status import ActionStatusEnum
from app.models.application import Application
from app.models.correlation_group import CorrelationGroup
from app.models.investigation import Investigation
from app.ml.feature_extractor import MISSING_VALUE_SENTINEL, extract_features
from app.services.action_queue_service import approve_action, create_actions
from app.services import evidence_service


class DummySession:
    def __init__(self):
        self.commits = 0
        self.refreshed = []

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        self.refreshed.append(obj)


def test_approve_action_marks_action_approved_before_execution(monkeypatch):
    db = DummySession()
    action = SimpleNamespace(
        status=ActionStatusEnum.PENDING,
        approved_by=None,
        execution_log=None,
    )

    def fake_execute_action(action_obj):
        assert action_obj.status == ActionStatusEnum.APPROVED
        return {"ok": True}

    monkeypatch.setattr(
        "app.services.action_queue_service.execute_action",
        fake_execute_action,
    )

    result = approve_action(
        db=db,
        action=action,
        approved_by=uuid.uuid4(),
    )

    assert result.status == ActionStatusEnum.EXECUTED
    assert action.status == ActionStatusEnum.EXECUTED


def test_extract_features_uses_missing_value_sentinel_for_null_metrics():
    evidence = SimpleNamespace(
        cpu_usage=None,
        memory_usage=10.0,
        disk_usage=None,
        disk_io_wait=None,
        api_latency=None,
        http_5xx_count=None,
        http_4xx_count=None,
        request_per_second=None,
        error_rate=None,
        db_connections=None,
        failed_login_attempts=None,
        packet_loss=None,
        network_latency=None,
        restart_count=None,
        active_containers=None,
        deployment_changed=None,
        ssl_certificate_days_left=None,
    )

    features = extract_features(evidence)

    assert features[0] == MISSING_VALUE_SENTINEL
    assert features[1] == 10.0
    assert features[2] == MISSING_VALUE_SENTINEL


def test_create_actions_uses_application_resource_uuid_when_target_missing():
    db = DummySession()
    investigation_id = uuid.uuid4()
    incident_id = uuid.uuid4()
    investigation = SimpleNamespace(id=investigation_id, incident=SimpleNamespace(id=incident_id))
    application = SimpleNamespace(resource_uuid="coolify-resource-123")

    class StubDB(DummySession):
        def __init__(self, investigation, application):
            super().__init__()
            self._investigation = investigation
            self._application = application
            self.added = []

        def add(self, obj):
            self.added.append(obj)

        def get(self, model, obj_id):
            if model is Investigation:
                return self._investigation
            if model is Application:
                return self._application
            return None

        def query(self, model):
            class Query:
                def filter(self, *args, **kwargs):
                    return self

                def order_by(self, *args, **kwargs):
                    return self

                def first(self):
                    if model is CorrelationGroup:
                        return SimpleNamespace(application_id=uuid.uuid4())
                    return None

            return Query()

    stub_db = StubDB(investigation, application)

    created = create_actions(
        db=stub_db,
        investigation_id=investigation_id,
        actions=[{"title": "Restart app", "action_type": "RESTART_APPLICATION"}],
        confidence=0.93,
    )

    assert len(created) == 1
    assert created[0].target == "coolify-resource-123"
    assert created[0].status == ActionStatusEnum.PENDING_APPROVAL


def test_build_evidence_from_group_populates_model_features_from_metrics(monkeypatch):
    group = SimpleNamespace(
        id=uuid.uuid4(),
        incident_id=uuid.uuid4(),
        application_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        server_id=uuid.uuid4(),
        first_seen=None,
        last_seen=None,
    )

    class DummyQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return [SimpleNamespace(timestamp=None, level="ERROR", message="boom", occurrence_count=1)]

        def first(self):
            return None

    class DummyDB:
        def get(self, model, obj_id):
            if model is Application:
                return SimpleNamespace(name="billing-api")
            return None

        def query(self, model):
            return DummyQuery()

    monkeypatch.setattr(evidence_service, "get_logs_for_group", lambda db, group_id: [SimpleNamespace(timestamp=None, level="ERROR", message="boom", occurrence_count=1)])
    monkeypatch.setattr(evidence_service, "aggregate_system_metrics", lambda db, group: {
        "cpu_usage": 12.5,
        "memory_usage": 34.0,
        "disk_usage": 55.0,
        "disk_io_wait": 0.8,
        "api_latency": 150,
        "http_5xx_count": 3,
        "http_4xx_count": 2,
        "request_per_second": 120.0,
    })

    evidence_data = evidence_service.build_evidence_from_group(db=DummyDB(), group=group)

    assert evidence_data["cpu_usage"] == 12.5
    assert evidence_data["memory_usage"] == 34.0
    assert evidence_data["disk_usage"] == 55.0
    assert evidence_data["disk_io_wait"] == 0.8
    assert evidence_data["api_latency"] == 150
    assert evidence_data["http_5xx_count"] == 3
    assert evidence_data["http_4xx_count"] == 2
    assert evidence_data["request_per_second"] == 120.0
    assert evidence_data["error_rate"] == 1.0
