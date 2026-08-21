from sqlalchemy.orm import Session

from app.models.correlation_group import CorrelationGroup

from app.schemas.investigation import (
    InvestigationCreate,
)

from app.services.correlation_incident_service import (
    create_incident_from_correlation_group,
)

from app.services.investigation_service import (
    create_investigation,
)


def create_investigation_from_group(
    db: Session,
    correlation_group: CorrelationGroup,
):
    """
    Complete flow:

    Correlation Group
            ↓
        Incident
            ↓
      Investigation

    ML and LLM execution happens inside
    create_investigation().
    """

    # ==========================================================
    # 1. Create / Get Incident
    # ==========================================================

    incident = create_incident_from_correlation_group(
        db=db,
        correlation_group=correlation_group,
    )

    if incident is None:
        return None

    # ==========================================================
    # 2. Create / Get Investigation
    # ==========================================================

    investigation_data = InvestigationCreate(

        incident_id=incident.id,

    )

    investigation = create_investigation(

        db=db,

        investigation_data=investigation_data,

    )

    return investigation
