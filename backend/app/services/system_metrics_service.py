from app.services.evidence_service import aggregate_system_metrics as _aggregate_system_metrics


def aggregate_system_metrics(*args, **kwargs):
    """Compatibility wrapper for system metric aggregation."""
    return _aggregate_system_metrics(*args, **kwargs)
