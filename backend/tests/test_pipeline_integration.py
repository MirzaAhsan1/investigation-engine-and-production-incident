from types import SimpleNamespace

from app.services.log_ingestion_service import ingest_log


class DummySession:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0
        self.added = []

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def flush(self):
        return None

    def refresh(self, obj):
        return None


def test_ingest_log_triggers_investigation_chain(monkeypatch):
    db = DummySession()

    def fake_get_client_by_api_key(**kwargs):
        return SimpleNamespace(id="client-1")

    def fake_get_server_by_host(**kwargs):
        return SimpleNamespace(id="server-1")

    def fake_get_application_by_container(**kwargs):
        return SimpleNamespace(id="app-1")

    def fake_is_interesting_log(level, message):
        return True, "Matched level: ERROR"

    def fake_generate_log_fingerprint(**kwargs):
        return "fingerprint"

    def fake_get_log_by_fingerprint(**kwargs):
        return None

    def fake_save_log(**kwargs):
        return SimpleNamespace(
            id="log-1",
            client_id="client-1",
            server_id="server-1",
            application_id="app-1",
            fingerprint="fingerprint",
            occurrence_count=1,
            first_seen="2024-01-01T00:00:00",
            last_seen="2024-01-01T00:00:00",
            correlation_group_id=None,
        )

    def fake_correlate_log(db, log):
        return SimpleNamespace(id="group-1", incident_id="incident-1")

    def fake_create_incident_from_group(db, group):
        return SimpleNamespace(id="incident-1")

    def fake_start_investigation(db, incident_id):
        return SimpleNamespace(id="investigation-1")

    monkeypatch.setattr("app.services.log_ingestion_service.get_client_by_api_key", fake_get_client_by_api_key)
    monkeypatch.setattr("app.services.log_ingestion_service.get_server_by_host", fake_get_server_by_host)
    monkeypatch.setattr("app.services.log_ingestion_service.get_application_by_container", fake_get_application_by_container)
    monkeypatch.setattr("app.services.log_ingestion_service.is_interesting_log", fake_is_interesting_log)
    monkeypatch.setattr("app.services.log_ingestion_service.generate_log_fingerprint", fake_generate_log_fingerprint)
    monkeypatch.setattr("app.services.log_ingestion_service.get_log_by_fingerprint", fake_get_log_by_fingerprint)
    monkeypatch.setattr("app.services.log_ingestion_service.save_log", fake_save_log)
    monkeypatch.setattr("app.services.log_ingestion_service.correlate_log", fake_correlate_log)
    monkeypatch.setattr("app.services.log_ingestion_service.create_incident_from_group", fake_create_incident_from_group)
    monkeypatch.setattr("app.services.log_ingestion_service.start_investigation", fake_start_investigation)

    log = SimpleNamespace(
        api_key="test-key",
        host="server-1",
        container_name="backend",
        level="ERROR",
        message="Database timeout occurred",
        timestamp="2024-01-01T00:00:00",
    )

    result = ingest_log(db=db, log=log)

    assert result["status"] == "interesting"
    assert result["incident_id"] == "incident-1"
    assert result["investigation_triggered"] is True
