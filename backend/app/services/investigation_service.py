from uuid import UUID

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.incident import Incident
from app.models.investigation import Investigation

from app.enums.analysis_status import (
    AnalysisStatusEnum,
)

from app.schemas.investigation import (
    InvestigationCreate,
)

from app.services.action_queue_service import (
    create_actions,
)

from app.services.ml_service import (
    predict_incident,
)

from app.services.report_generator import (
    build_report,
)

from app.ai.llm_service import (
    investigate,
)


MODEL_VERSION = "v2.0"


def create_investigation(
    db: Session,
    investigation_data: InvestigationCreate,
):
    """
    Stable investigation pipeline.

    Incident
        ↓
    Evidence
        ↓
    ML
        ↓
    LLM
        ↓
    Investigation
        ↓
    Actions
    """

    # ========================================================
    # 1. Incident
    # ========================================================

    incident = db.get(
        Incident,
        investigation_data.incident_id,
    )

    if incident is None:
        return None

    # ========================================================
    # 2. Existing Investigation
    # ========================================================

    existing = (
        db.query(Investigation)
        .filter(
            Investigation.incident_id
            == incident.id,
        )
        .first()
    )

    if existing is not None:
        return existing

    # ========================================================
    # 3. Evidence
    # ========================================================

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.incident_id
            == incident.id,
        )
        .first()
    )

    if evidence is None:
        return None

    # ========================================================
    # 4. ML Prediction
    # ========================================================

    prediction = predict_incident(db=db, incident_id=incident.id)

    if not prediction:
        return None

    # ========================================================
    # 5. LLM Investigation
    # ========================================================

    llm_result = investigate(
        incident=incident,
        evidence=evidence,
        prediction=prediction,
    )

    if not llm_result:
        return None

    # ========================================================
    # 6. ML Results
    # ========================================================

    predicted_category = (
        prediction.get(
            "predicted_category",
            "UNKNOWN",
        )
    )

    predicted_cause = (
        prediction.get(
            "predicted_cause",
            "UNKNOWN",
        )
    )

    confidence = float(
        prediction.get(
            "confidence",
            0.0,
        )
    )

    # ========================================================
    # 7. LLM Results
    # ========================================================

    root_cause = llm_result.get(
        "root_cause",
        predicted_cause,
    )

    reasoning = llm_result.get(
        "reasoning",
        "",
    )

    recommended_actions = (
        llm_result.get(
            "recommended_actions",
            [],
        )
    )

    llm_confidence = float(
        llm_result.get(
            "llm_confidence",
            confidence,
        )
    )

    # ========================================================
    # 8. Normalize Actions
    # ========================================================

    action_titles = []

    for action in recommended_actions:

        if isinstance(action, dict):

            title = action.get(
                "title"
            )

            if title:
                action_titles.append(
                    title
                )

        elif isinstance(action, str):

            action_titles.append(
                action
            )

    # ========================================================
    # 9. Create Investigation
    # ========================================================

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
    # 10. Action Queue
    # ========================================================

    if recommended_actions:

        create_actions(
            db=db,

            investigation_id=(
                investigation.id
            ),

            actions=recommended_actions,

            confidence=confidence,
        )

    # ========================================================
    # 11. Commit
    # ========================================================

    db.commit()

    db.refresh(
        investigation
    )

    return investigation


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


def get_full_report(
    db: Session,
    incident_id: UUID,
):

    incident = db.get(
        Incident,
        incident_id,
    )

    if incident is None:
        return None

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.incident_id
            == incident_id,
        )
        .first()
    )

    if evidence is None:
        return None

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

    return build_report(
        incident,
        evidence,
        investigation,
    )