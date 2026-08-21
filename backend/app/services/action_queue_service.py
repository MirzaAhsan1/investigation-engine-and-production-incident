from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.execution_service import execute_action

from app.enums.action_status import ActionStatusEnum
from app.models.action_queue import ActionQueue
from app.models.application import Application
from app.models.correlation_group import CorrelationGroup
from app.models.investigation import Investigation


# ==========================================================
# Resolve Action Target
# ==========================================================

def _resolve_action_target(
    db: Session,
    investigation_id,
    action,
):
    """
    Resolve the Coolify target for an action.

    Priority:
    1. Use target supplied by LLM if valid.
    2. Otherwise use application's stored resource UUID.
    """

    # ------------------------------------------------------
    # 1. Target supplied by LLM
    # ------------------------------------------------------

    if isinstance(action, dict):

        target = str(
            action.get("target", "")
        ).strip()

        if target:
            # Keep target reasonably sized
            return target[:255]

    # ------------------------------------------------------
    # 2. Load Investigation
    # ------------------------------------------------------

    investigation = db.get(
        Investigation,
        investigation_id,
    )

    if investigation is None:
        return ""

    # ------------------------------------------------------
    # 3. Get Incident ID
    # ------------------------------------------------------

    incident_id = getattr(
        investigation,
        "incident_id",
        None,
    )

    if incident_id is None:

        incident = getattr(
            investigation,
            "incident",
            None,
        )

        incident_id = getattr(
            incident,
            "id",
            None,
        )

    if incident_id is None:
        return ""

    # ------------------------------------------------------
    # 4. Find Correlation Group
    # ------------------------------------------------------

    correlation_group = (
        db.query(CorrelationGroup)
        .filter(
            CorrelationGroup.incident_id
            == incident_id
        )
        .order_by(
            CorrelationGroup.last_seen.desc()
        )
        .first()
    )

    if correlation_group is None:
        return ""

    # ------------------------------------------------------
    # 5. Load Application
    # ------------------------------------------------------

    application = db.get(
        Application,
        correlation_group.application_id,
    )

    if application is None:
        return ""

    # ------------------------------------------------------
    # 6. Return Coolify Resource UUID
    # ------------------------------------------------------

    return str(
        getattr(
            application,
            "resource_uuid",
            "",
        ) or ""
    )[:255]


# ==========================================================
# Create Actions
# ==========================================================

def create_actions(
    db: Session,
    investigation_id,
    actions,
    confidence,
):
    """
    Create ActionQueue records.

    IMPORTANT:
    This function does NOT commit.
    The caller controls the transaction.
    """

    created = []

    # ------------------------------------------------------
    # Validate actions container
    # ------------------------------------------------------

    if not isinstance(actions, list):
        return created

    # ------------------------------------------------------
    # Process each action
    # ------------------------------------------------------

    for action in actions:

        # ==================================================
        # Only structured dictionary actions are accepted
        # ==================================================

        if not isinstance(action, dict):

            print(
                "[ACTION QUEUE] Skipping invalid "
                "non-dictionary action."
            )

            continue

        # ==================================================
        # Extract fields
        # ==================================================

        title = str(
            action.get(
                "title",
                "",
            )
        ).strip()

        action_type = str(
            action.get(
                "action_type",
                "",
            )
        ).strip()

        # ==================================================
        # Validate required fields
        # ==================================================

        if not title:

            print(
                "[ACTION QUEUE] Skipping action "
                "because title is empty."
            )

            continue

        if not action_type:

            print(
                "[ACTION QUEUE] Skipping action "
                "because action_type is empty."
            )

            continue

        # ==================================================
        # Protect VARCHAR columns
        # ==================================================

        # action_type DB column = VARCHAR(100)
        if len(action_type) > 100:

            print(
                "[ACTION QUEUE] Skipping action because "
                "action_type exceeds 100 characters."
            )

            continue

        # Assuming title/target are VARCHAR(255)
        title = title[:255]

        # ==================================================
        # Priority
        # ==================================================

        priority = action.get(
            "priority",
            999,
        )

        try:

            priority = int(priority)

        except (
            TypeError,
            ValueError,
        ):

            priority = 999

        # ==================================================
        # Resolve target
        # ==================================================

        target = _resolve_action_target(
            db=db,
            investigation_id=investigation_id,
            action=action,
        )

        # ==================================================
        # Create queue record
        # ==================================================

        queue = ActionQueue(

            investigation_id=investigation_id,

            title=title,

            action_type=action_type,

            target=target,

            priority=priority,

            confidence=confidence,

            status=(
                ActionStatusEnum.PENDING_APPROVAL
            ),
        )

        db.add(queue)

        created.append(queue)

    return created


# ==========================================================
# Get Actions
# ==========================================================

def get_actions_by_investigation(
    db: Session,
    investigation_id: UUID,
):

    return (
        db.query(ActionQueue)
        .filter(
            ActionQueue.investigation_id
            == investigation_id
        )
        .order_by(
            ActionQueue.priority
        )
        .all()
    )


# ==========================================================
# Get Single Action
# ==========================================================

def get_action(
    db: Session,
    action_id: UUID,
):

    return db.get(
        ActionQueue,
        action_id,
    )


# ==========================================================
# Get Actions By Incident
# ==========================================================

def get_actions_by_incident(
    db: Session,
    incident_id: UUID,
):
    investigation = (
        db.query(Investigation)
        .filter(Investigation.incident_id == incident_id)
        .first()
    )

    if investigation is None:
        return []

    return get_actions_by_investigation(db, investigation.id)


# ==========================================================
# Update Action Status (Approve/Deny)
# ==========================================================

def update_action_status(
    db: Session,
    action: ActionQueue,
    new_status: ActionStatusEnum,
    approved_by: UUID | None = None,
):
    """
    Update action status in DB (APPROVED or REJECTED).

    CURRENT BEHAVIOR (dummy / placeholder execution):

        On APPROVE, this does NOT call the real execution
        engine (execute_action / Coolify). Instead it
        simulates execution: it writes a fake
        execution_log and marks the action as EXECUTED,
        so the UI shows a completed lifecycle end-to-end
        without touching any real infrastructure.

    # TODO: Real execution hook point.
    # When automated action execution is ready to go live,
    # replace the dummy block below with a real call to
    # execute_action(action), following the same
    # try/except/rollback/FAILED pattern used previously
    # (see execute_action import above, currently unused
    # here on purpose).
    """

    try:

        if approved_by is not None:
            action.approved_by = approved_by

        if new_status == ActionStatusEnum.APPROVED:

            # ------------------------------------------------
            # DUMMY EXECUTION (placeholder only)
            #
            # No real infrastructure call is made here.
            # ------------------------------------------------

            action.status = ActionStatusEnum.EXECUTED

            action.execution_log = (
                "[DUMMY] Simulated execution — no real "
                f"action performed. action_type={action.action_type}, "
                f"target={action.target}, "
                f"simulated_at={datetime.now(timezone.utc).isoformat()}"
            )

            print(
                "[ACTION QUEUE] Dummy execution recorded "
                f"for action {action.id} "
                f"({action.action_type} -> {action.target})"
            )

        else:

            action.status = new_status

        db.commit()

        db.refresh(action)

        return action

    except Exception:

        db.rollback()

        raise