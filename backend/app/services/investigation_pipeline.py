from uuid import UUID

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.incident import Incident
from app.models.investigation import Investigation

from app.enums.analysis_status import AnalysisStatusEnum

from app.services.action_queue_service import create_actions
from app.services.ml_service import predict_incident
from app.services.report_generator import build_report

from app.ai.llm_service import investigate


MODEL_VERSION = "v2.0"


# ============================================================
# START INVESTIGATION
# ============================================================

def start_investigation(
    db: Session,
    incident_id: UUID,
):
    """
    Start (or refresh) the AI investigation for an incident.

    Phase 2 Flow:

        Incident
           +
        Latest Evidence
           ↓
        ML Prediction
           ↓
        LLM Investigation
           ↓
        Investigation Record (create OR update)
           ↓
        Action Queue

    NOTE:

    Evidence is one-to-many with Incident: an incident can
    accumulate multiple Evidence rows over time (e.g. when
    the same application keeps generating related
    correlation groups and the incident is reused instead
    of a brand new one being created).

    Investigation stays one-to-one with Incident: if an
    Investigation already exists for this incident, it is
    UPDATED with a fresh ML + LLM run using the latest
    Evidence, rather than being skipped. This keeps the
    diagnosis current as new signal comes in, instead of
    freezing on the first analysis.
    """

    # ========================================================
    # 1. Get Incident
    # ========================================================

    incident = db.get(
        Incident,
        incident_id,
    )

    if incident is None:
        return None

    # ========================================================
    # 2. Get Latest Evidence
    #
    # Evidence is one-to-many with Incident now, so we take
    # the most recently created row.
    # ========================================================

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.incident_id
            == incident.id,
        )
        .order_by(
            Evidence.created_at.desc(),
        )
        .first()
    )

    if evidence is None:
        return None

    # ========================================================
    # 3. Check For Existing Investigation
    #
    # If one already exists, we will UPDATE it below instead
    # of creating a duplicate (Investigation.incident_id is
    # still unique).
    # ========================================================

    existing_investigation = (
        db.query(Investigation)
        .filter(
            Investigation.incident_id
            == incident.id,
        )
        .first()
    )

    # ========================================================
    # 4. ML Prediction
    #
    # ML receives BOTH:
    #
    # Incident
    # Latest Evidence
    # ========================================================

    prediction = predict_incident(
        incident=incident,
        evidence=evidence,
    )

    if not prediction:

        print(
            "[ML] No prediction returned "
            f"for incident {incident_id}"
        )

        return existing_investigation

    print(
        "[ML] Prediction completed "
        f"for incident {incident_id}: "
        f"{prediction}"
    )

    # ========================================================
    # 5. Extract ML Results
    # ========================================================

    predicted_category = prediction.get(
        "predicted_category",
        "UNKNOWN",
    )

    predicted_cause = prediction.get(
        "predicted_cause",
        "UNKNOWN",
    )

    confidence = float(
        prediction.get(
            "confidence",
            0.0,
        )
    )

    # ========================================================
    # 6. LLM Investigation
    #
    # LLM receives:
    #
    # Incident
    # Latest Evidence
    # ML Prediction
    # ========================================================

    llm_result = investigate(
        incident=incident,
        evidence=evidence,
        prediction=prediction,
    )

    if not llm_result:

        print(
            "[LLM] No investigation result "
            f"for incident {incident_id}"
        )

        return existing_investigation

    print(
        "[LLM] Investigation completed "
        f"for incident {incident_id}: "
        f"root_cause={llm_result.get('root_cause')}, "
        f"llm_confidence={llm_result.get('llm_confidence')}"
    )

    # ========================================================
    # 7. Extract LLM Results
    # ========================================================

    root_cause = llm_result.get(
        "root_cause",
        predicted_cause,
    )

    reasoning = llm_result.get(
        "reasoning",
        "",
    )

    recommended_actions = llm_result.get(
        "recommended_actions",
        [],
    )

    llm_confidence = float(
        llm_result.get(
            "llm_confidence",
            0.0,
        )
    )

    # ========================================================
    # 8. Normalize Actions
    # ========================================================

    normalized_actions = []

    for action in recommended_actions:

        if not isinstance(action, dict):
            continue

        title = str(
            action.get(
                "title",
                "",
            )
        ).strip()

        if not title:
            continue

        normalized_actions.append(
            {
                "title": title[:255],

                "action_type": str(
                    action.get(
                        "action_type",
                        "",
                    )
                ).strip()[:100],

                "target": str(
                    action.get(
                        "target",
                        "",
                    )
                ).strip()[:255],

                "priority": int(
                    action.get(
                        "priority",
                        999,
                    )
                ),
            }
        )

    # ========================================================
    # 9. Convert Actions to Text
    #
    # Investigation table stores recommended_actions
    # as text, while ActionQueue stores structured actions.
    # ========================================================

    action_titles = [
        action["title"]
        for action in normalized_actions
    ]

    # ========================================================
    # 10. Create OR Update Investigation
    # ========================================================

    if existing_investigation is not None:

        # ----------------------------------------------------
        # Update in place — keeps the one-to-one relationship
        # with Incident, but refreshes the diagnosis using
        # the latest evidence instead of freezing on the
        # first analysis.
        # ----------------------------------------------------

        investigation = existing_investigation

        investigation.predicted_category = predicted_category
        investigation.predicted_cause = predicted_cause
        investigation.confidence = confidence
        investigation.model_version = MODEL_VERSION
        investigation.risk_score = confidence
        investigation.root_cause = root_cause
        investigation.reasoning = reasoning
        investigation.recommended_actions = "\n".join(action_titles)
        investigation.llm_confidence = llm_confidence
        investigation.analysis_status = AnalysisStatusEnum.COMPLETED

        print(
            "[INVESTIGATION] Updated existing investigation "
            f"for incident {incident_id}: "
            f"investigation_id={investigation.id}"
        )

    else:

        investigation = Investigation(

            incident_id=incident.id,

            predicted_category=(
                predicted_category
            ),

            predicted_cause=(
                predicted_cause
            ),

            confidence=confidence,

            model_version=MODEL_VERSION,

            risk_score=confidence,

            root_cause=root_cause,

            reasoning=reasoning,

            recommended_actions=(
                "\n".join(
                    action_titles
                )
            ),

            llm_confidence=(
                llm_confidence
            ),

            triggered_rules=[],

            analysis_status=(
                AnalysisStatusEnum.COMPLETED
            ),
        )

        db.add(
            investigation
        )

    db.flush()

    # ========================================================
    # 11. Create Action Queue
    #
    # NOTE: on an update (re-investigation of a reused
    # incident), this ADDS new actions alongside any earlier
    # ones rather than replacing them. Older pending actions
    # are left as-is for the operator to review/reject
    # manually.
    # ========================================================

    if normalized_actions:

        create_actions(
            db=db,

            investigation_id=(
                investigation.id
            ),

            actions=normalized_actions,

            confidence=confidence,
        )

    # ========================================================
    # 12. Commit
    # ========================================================

    db.commit()

    db.refresh(
        investigation
    )

    print(
        "[INVESTIGATION] Completed "
        f"for incident {incident_id}: "
        f"investigation_id={investigation.id}, "
        f"actions_queued={len(normalized_actions)}"
    )

    return investigation


# ============================================================
# GET INVESTIGATION BY INCIDENT
# ============================================================

def get_investigation_by_incident(
    db: Session,
    incident_id: UUID,
):

    return (
        db.query(
            Investigation
        )
        .filter(
            Investigation.incident_id
            == incident_id,
        )
        .first()
    )


# ============================================================
# GET COMPLETE INVESTIGATION REPORT
# ============================================================

def get_full_report(
    db: Session,
    incident_id: UUID,
):

    # ========================================================
    # Incident
    # ========================================================

    incident = db.get(
        Incident,
        incident_id,
    )

    if incident is None:
        return None

    # ========================================================
    # Latest Evidence
    # ========================================================

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.incident_id
            == incident_id,
        )
        .order_by(
            Evidence.created_at.desc(),
        )
        .first()
    )

    if evidence is None:
        return None

    # ========================================================
    # Investigation
    # ========================================================

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.incident_id
            == incident_id,
        )
        .first()
    )

    if investigation is None:
        return None

    # ========================================================
    # Build Final Report
    # ========================================================

    return build_report(
        incident=incident,
        evidence=evidence,
        investigation=investigation,
    )