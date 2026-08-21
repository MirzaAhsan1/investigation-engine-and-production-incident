from sqlalchemy.orm import Session

from app.models.correlation_group import CorrelationGroup
from app.models.incident import Incident


def create_incident_from_correlation_group(
    db: Session,
    correlation_group: CorrelationGroup,
):
    """
    Create an Incident from a CorrelationGroup.

    One correlation group should normally represent
    one real production event/incident.
    """

    # ==========================================================
    # 1. Check if incident already exists
    # ==========================================================

    existing_incident = (
        db.query(Incident)
        .filter(
            Incident.correlation_group_id
            == correlation_group.id
        )
        .first()
    )

    if existing_incident is not None:
        return existing_incident

    # ==========================================================
    # 2. Build Incident title
    # ==========================================================

    title = (
        correlation_group.primary_message
        or "Production Incident Detected"
    )

    # ==========================================================
    # 3. Build Incident description
    # ==========================================================

    description = (
        f"Incident detected from correlated logs. "
        f"Correlation group contains "
        f"{correlation_group.event_count} related events."
    )

    # ==========================================================
    # 4. Create Incident
    # ==========================================================

    incident = Incident(

        title=title,

        description=description,

        incident_type="APPLICATION",

        severity="HIGH",

        status="OPEN",

        source="MONITORING",

        reported_by=correlation_group.client_id,

        correlation_group_id=correlation_group.id,

    )

    db.add(incident)

    db.flush()

    return incident
