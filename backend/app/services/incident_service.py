from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.correlation_group import CorrelationGroup
from app.models.incident import Incident
from app.models.evidence import Evidence
from app.models.user import User

from app.models.enums import (
    StatusEnum,
    IncidentSourceEnum,
    SeverityEnum,
    IncidentTypeEnum,
)
from app.services.application_service import (
    get_application,
)
# from app.services.application_service import (
#     get_application_by_id,
# )

from app.schemas.incident import IncidentCreate

# from app.services.evidence_aggregation_service import (
#     aggregate_evidence_for_incident,
# )

from app.core.security import hash_password


SYSTEM_USER_EMAIL = "system@monitor.local"


# ============================================================
# System User
# ============================================================

def get_or_create_system_user(
    db: Session,
):
    user = (
        db.query(User)
        .filter(
            User.email == SYSTEM_USER_EMAIL
        )
        .first()
    )

    if user is not None:
        return user

    user = User(
        full_name="System Monitor",
        email=SYSTEM_USER_EMAIL,
        password_hash=hash_password(
            "SystemSecurePass123!"
        ),
    )

    db.add(user)

    db.flush()

    return user


# ============================================================
# Create Incident From Correlation Group + Evidence
# ============================================================


def create_incident_from_group(
    db: Session,
    group: CorrelationGroup,
    evidence: Evidence,
):
    """
    Create exactly one Incident from:

        CorrelationGroup
              +
           Evidence
              +
        Application
              ↓
           Incident

    Evidence is created before Incident, therefore
    evidence.incident_id is NULL initially.

    After Incident creation, Evidence is linked
    to the newly created Incident.
    """

    # ========================================================
    # 1. Validate Correlation Group
    # ========================================================

    if group is None:
        return None

    # ========================================================
    # 2. Validate Evidence
    # ========================================================

    if evidence is None:
        return None

    # ========================================================
    # 3. Check Existing Incident
    # ========================================================

    if group.incident_id is not None:

        existing_incident = db.get(
            Incident,
            group.incident_id,
        )

        if existing_incident is not None:

            # ------------------------------------------------
            # Make sure Evidence is linked
            # ------------------------------------------------

            if evidence.incident_id != existing_incident.id:

                evidence.incident_id = (
                    existing_incident.id
                )

                db.flush()

            return existing_incident

    # ========================================================
    # 4. System User
    # ========================================================

    system_user = get_or_create_system_user(
        db=db,
    )

    # ========================================================
    # 5. Create Incident
    # ========================================================

    incident = Incident(

        title=(
            "Production incident detected "
            f"for {group.application_id}"
        ),

        description=(
            "Incident created from correlated "
            f"production logs. "
            f"Correlation group contains "
            f"{group.event_count} related event(s) "
            f"between {group.first_seen} "
            f"and {group.last_seen}."
        ),

        incident_type=(
            IncidentTypeEnum.APPLICATION
        ),

        severity=(
            SeverityEnum.HIGH
        ),

        status=(
            StatusEnum.OPEN
        ),

        source=(
            IncidentSourceEnum.MONITORING
        ),

        reported_by=system_user.id,

        # ----------------------------------------------------
        # Application / Container
        # ----------------------------------------------------

        application_id=(
            group.application_id
        ),
    )

    db.add(incident)

    db.flush()

    # ========================================================
    # 6. Link CorrelationGroup → Incident
    # ========================================================

    group.incident_id = incident.id

    db.flush()

    # ========================================================
    # 7. Link Evidence → Incident
    # ========================================================

    evidence.incident_id = incident.id

    db.flush()

    return incident


# ============================================================
# Get All Incidents
# ============================================================

def get_all_incidents(
    db: Session,
):
    """
    Return all incidents sorted by most recent first.

    Application and Investigation relationships are eager-loaded.
    """

    return (
        db.query(Incident)
        .options(
            joinedload(
                Incident.application
            ),
            joinedload(
                Incident.investigation
            ),
        )
        .order_by(
            Incident.created_at.desc()
        )
        .all()
    )


# ============================================================
# Get Incident Detail
# ============================================================


def get_incident_detail(
    db: Session,
    incident_id: UUID,
):

#   """
#     Get complete incident detail.

#     Flow:

#         Incident
#             ↓
#         Application / Container
#             +
#         CorrelationGroup
#             +
#         Evidence
#     """

    incident = db.get(
        Incident,
        incident_id,
    )

    if incident is None:
        return None

    application = None

    if incident.application_id is not None:

        application = get_application(
            db=db,
            application_id=incident.application_id,
        )

    correlation_group = (
        db.query(CorrelationGroup)
        .filter(
            CorrelationGroup.incident_id
            == incident.id
        )
        .order_by(
            CorrelationGroup.last_seen.desc()
        )
        .first()
    )

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.incident_id
            == incident.id
        )
        .first()
    )

    return {
        "incident": incident,
        "application": application,
        "correlation_group": correlation_group,
        "evidence": evidence,
    }

# ============================================================
# Manual Incident Creation
# ============================================================

def create_incident(
    db: Session,
    incident_data: IncidentCreate,
    current_user: User,
) -> Incident:

    incident = Incident(
        title=incident_data.title,

        description=incident_data.description,

        severity=incident_data.severity,

        incident_type=incident_data.incident_type,

        source=incident_data.source,

        status=StatusEnum.OPEN,

        reported_by=current_user.id,
    )

    db.add(incident)

    db.commit()

    db.refresh(incident)

    return incident