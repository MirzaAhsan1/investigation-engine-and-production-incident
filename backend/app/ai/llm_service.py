import json
import re

from app.ai.prompt_builder import build_prompt
from app.ai.llm_client import LLMClient


client = LLMClient()


# ==========================================================
# Normalize LLM Actions
# ==========================================================

def _normalize_actions(actions):
    """
    Validate and normalize LLM-generated actions.

    Expected action format:

    {
        "title": "...",
        "action_type": "...",
        "target": "...",
        "priority": 1
    }

    Only structured dictionary actions are accepted.
    """

    if not isinstance(actions, list):
        return []

    normalized = []

    for action in actions:

        # --------------------------------------------------
        # Only dictionaries allowed
        # --------------------------------------------------

        if not isinstance(action, dict):
            continue

        # --------------------------------------------------
        # Extract fields
        # --------------------------------------------------

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

        target = str(
            action.get(
                "target",
                "",
            )
        ).strip()

        priority = action.get(
            "priority",
            999,
        )

        # --------------------------------------------------
        # Required fields
        # --------------------------------------------------

        if not title:
            continue

        if not action_type:
            continue

        # --------------------------------------------------
        # Protect DB VARCHAR limits
        # --------------------------------------------------

        title = title[:255]

        action_type = action_type[:100]

        target = target[:255]

        # --------------------------------------------------
        # Normalize priority
        # --------------------------------------------------

        try:

            priority = int(
                priority
            )

        except (
            TypeError,
            ValueError,
        ):

            priority = 999

        # --------------------------------------------------
        # Keep priority reasonable
        # --------------------------------------------------

        if priority < 1:
            priority = 1

        # --------------------------------------------------
        # Store clean action
        # --------------------------------------------------

        normalized.append(
            {
                "title": title,
                "action_type": action_type,
                "target": target,
                "priority": priority,
            }
        )

    # ------------------------------------------------------
    # Sort actions by priority
    # ------------------------------------------------------

    normalized.sort(
        key=lambda action: action["priority"]
    )

    return normalized


# ==========================================================
# Safe ML Fallback
# ==========================================================

def _ml_fallback(
    prediction,
    reason,
):
    """
    Return a safe fallback when LLM investigation
    cannot be completed.
    """

    prediction = (
        prediction
        if isinstance(prediction, dict)
        else {}
    )

    prediction_category = prediction.get(
        "predicted_category",
        "UNKNOWN",
    )

    prediction_cause = prediction.get(
        "predicted_cause",
        "UNKNOWN",
    )

    return {
        "root_cause": prediction_cause,

        "reasoning": (
            f"{reason} "
            "The pipeline therefore used the ML "
            "prediction as the current probable cause. "
            f"Predicted category: "
            f"'{prediction_category}'. "
            f"Predicted cause: "
            f"'{prediction_cause}'."
        ),

        "llm_confidence": 0.0,

        "recommended_actions": [],
    }


# ==========================================================
# Clean LLM JSON
# ==========================================================

def _extract_json(response):
    """
    Extract JSON object from an LLM response.

    Handles responses such as:

        ```json
        {...}
        ```

    or:

        {...}
    """

    if not response:
        return None

    cleaned = response.strip()

    # ------------------------------------------------------
    # Remove markdown code fences
    # ------------------------------------------------------

    cleaned = re.sub(
        r"^```(?:json)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"```$",
        "",
        cleaned,
    )

    cleaned = cleaned.strip()

    # ------------------------------------------------------
    # Find JSON object
    # ------------------------------------------------------

    match = re.search(
        r"\{.*\}",
        cleaned,
        re.DOTALL,
    )

    if not match:
        return None

    return match.group(0)


# ==========================================================
# LLM Investigation
# ==========================================================

def investigate(
    incident,
    evidence,
    prediction,
):
    """
    Investigate an Incident using:

        Incident
            +
        Evidence
            +
        ML Prediction
            ↓
        LLM

    Returns:

        root_cause
        reasoning
        llm_confidence
        recommended_actions
    """

    # ======================================================
    # 1. Validate Input
    # ======================================================

    if incident is None:

        return _ml_fallback(
            prediction=prediction,
            reason=(
                "Incident information was not available."
            ),
        )

    if evidence is None:

        return _ml_fallback(
            prediction=prediction,
            reason=(
                "Evidence information was not available."
            ),
        )

    if not isinstance(
        prediction,
        dict,
    ):

        return _ml_fallback(
            prediction={},
            reason=(
                "ML prediction was not available."
            ),
        )

    # ======================================================
    # 2. Build Prompt
    # ======================================================

    try:

        prompt = build_prompt(
            incident=incident,
            evidence=evidence,
            prediction=prediction,
        )

    except Exception as exc:

        print(
            "[LLM ERROR] Prompt building failed: "
            f"{exc}"
        )

        return _ml_fallback(
            prediction=prediction,
            reason=(
                "The investigation prompt could not "
                "be generated."
            ),
        )

    # ======================================================
    # 3. Call LLM
    # ======================================================

    try:

        response = client.generate(
            prompt
        )

    except Exception as exc:

        print(
            "[LLM ERROR] LLM request failed: "
            f"{exc}"
        )

        return _ml_fallback(
            prediction=prediction,
            reason=(
                "The LLM service was unavailable."
            ),
        )

    # ======================================================
    # 4. Extract JSON
    # ======================================================

    json_text = _extract_json(
        response
    )

    if json_text is None:

        print(
            "[LLM WARNING] No valid JSON object "
            "found in LLM response."
        )

        cleaned_response = (
            response.strip()
            if response
            else ""
        )

        return {
            "root_cause": prediction.get(
                "predicted_cause",
                "Unknown",
            ),

            "reasoning": (
                cleaned_response
                or
                "LLM returned no usable investigation result."
            ),

            "llm_confidence": 0.0,

            "recommended_actions": [],
        }

    # ======================================================
    # 5. Parse JSON
    # ======================================================

    try:

        result = json.loads(
            json_text
        )

    except json.JSONDecodeError as exc:

        print(
            "[LLM WARNING] Invalid JSON returned "
            f"by LLM: {exc}"
        )

        return {
            "root_cause": prediction.get(
                "predicted_cause",
                "Unknown",
            ),

            "reasoning": (
                "The LLM returned an invalid JSON "
                "investigation result."
            ),

            "llm_confidence": 0.0,

            "recommended_actions": [],
        }

    # ======================================================
    # 6. Ensure Result Is Dictionary
    # ======================================================

    if not isinstance(
        result,
        dict,
    ):

        return _ml_fallback(
            prediction=prediction,
            reason=(
                "The LLM response was not a JSON object."
            ),
        )

    # ======================================================
    # 7. Root Cause
    # ======================================================

    root_cause = str(
        result.get(
            "root_cause",
            prediction.get(
                "predicted_cause",
                "Unknown",
            ),
        )
    ).strip()

    if not root_cause:

        root_cause = prediction.get(
            "predicted_cause",
            "Unknown",
        )

    # ======================================================
    # 8. Reasoning
    # ======================================================

    reasoning = str(
        result.get(
            "reasoning",
            "",
        )
    ).strip()

    if not reasoning:

        reasoning = (
            "No detailed reasoning was returned "
            "by the LLM."
        )

    # ======================================================
    # 9. LLM Confidence
    # ======================================================

    try:

        llm_confidence = float(
            result.get(
                "llm_confidence",
                0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        llm_confidence = 0.0

    # ------------------------------------------------------
    # Normalize confidence to 0-100
    # ------------------------------------------------------

    if 0 <= llm_confidence <= 1:

        llm_confidence *= 100

    llm_confidence = max(
        0.0,
        min(
            llm_confidence,
            100.0,
        ),
    )

    llm_confidence = round(
        llm_confidence,
        2,
    )

    # ======================================================
    # 10. Recommended Actions
    # ======================================================

    recommended_actions = (
        _normalize_actions(
            result.get(
                "recommended_actions",
                [],
            )
        )
    )

    # ======================================================
    # 11. Final Result
    # ======================================================

    return {
        "root_cause": root_cause,

        "reasoning": reasoning,

        "llm_confidence": llm_confidence,

        "recommended_actions": (
            recommended_actions
        ),
    }