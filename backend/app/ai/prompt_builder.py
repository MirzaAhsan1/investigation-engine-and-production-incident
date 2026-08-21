from app.models.incident import Incident
from app.models.evidence import Evidence


def _value(value):
    """
    Safely return enum values / normal values.
    """
    if value is None:
        return "NOT_AVAILABLE"

    return getattr(
        value,
        "value",
        value,
    )


def build_prompt(
    incident: Incident,
    evidence: Evidence,
    prediction: dict,
) -> str:
    """
    Build a compact production incident investigation prompt.

    Priority:

        Evidence > ML Prediction

    The ML prediction is only an initial hypothesis.
    """

    prediction = (
        prediction
        if isinstance(prediction, dict)
        else {}
    )

    predicted_category = prediction.get(
        "predicted_category",
        "UNKNOWN",
    )

    predicted_cause = prediction.get(
        "predicted_cause",
        "UNKNOWN",
    )

    category_confidence = prediction.get(
        "category_confidence",
        0,
    )

    cause_confidence = prediction.get(
        "cause_confidence",
        0,
    )

    confidence = prediction.get(
        "confidence",
        0,
    )

    model_version = prediction.get(
        "model_version",
        "UNKNOWN",
    )

    return f"""
You are a Senior Site Reliability Engineer investigating
a production incident.

Your job is to determine the most likely root cause using:

1. Incident context
2. Observed Evidence
3. Real logs
4. ML prediction

IMPORTANT:

Evidence is the primary source of truth.

ML prediction is only a hypothesis.

Do not blindly trust the ML prediction.

Do not invent missing data.

Return ONLY valid JSON.

==================================================
INCIDENT
==================================================

ID:
{_value(incident.id)}

Title:
{_value(incident.title)}

Description:
{_value(incident.description)}

Severity:
{_value(incident.severity)}

Type:
{_value(incident.incident_type)}

Status:
{_value(incident.status)}

Source:
{_value(incident.source)}

==================================================
SERVICE
==================================================

Service:
{_value(evidence.service_name)}

Environment:
{_value(evidence.environment)}

First Seen:
{_value(evidence.first_seen)}

Last Seen:
{_value(evidence.last_seen)}

==================================================
LOG SUMMARY
==================================================

Log Count:
{_value(evidence.log_count)}

Error Count:
{_value(evidence.error_count)}

Warning Count:
{_value(evidence.warning_count)}

Error Rate:
{_value(evidence.error_rate)}

Database Timeout Count:
{_value(evidence.database_timeout_count)}

==================================================
INFRASTRUCTURE
==================================================

CPU:
{_value(evidence.cpu_usage)} %

Memory:
{_value(evidence.memory_usage)} %

Disk:
{_value(evidence.disk_usage)} %

Disk IO Wait:
{_value(evidence.disk_io_wait)} %

Network Latency:
{_value(evidence.network_latency)} ms

Packet Loss:
{_value(evidence.packet_loss)} %

==================================================
APPLICATION
==================================================

API Latency:
{_value(evidence.api_latency)} ms

Requests Per Second:
{_value(evidence.request_per_second)}

HTTP 5xx:
{_value(evidence.http_5xx_count)}

HTTP 4xx:
{_value(evidence.http_4xx_count)}

Restart Count:
{_value(evidence.restart_count)}

Pod Restart Count:
{_value(evidence.pod_restart_count)}

Active Containers:
{_value(evidence.active_containers)}

Deployment Changed:
{_value(evidence.deployment_changed)}

==================================================
DATABASE
==================================================

Connections:
{_value(evidence.db_connections)}

Timeouts:
{_value(evidence.database_timeout_count)}

==================================================
SECURITY
==================================================

Failed Login Attempts:
{_value(evidence.failed_login_attempts)}

SSL Days Remaining:
{_value(evidence.ssl_certificate_days_left)}

==================================================
LOGS
==================================================

{_value(evidence.logs)}

==================================================
ML HYPOTHESIS
==================================================

Model:
{model_version}

Category:
{predicted_category}

Cause:
{predicted_cause}

Category Confidence:
{category_confidence} %

Cause Confidence:
{cause_confidence} %

Overall Confidence:
{confidence} %

==================================================
TASK
==================================================

Analyze the incident using the evidence.

Determine:

1. Most likely root cause.
2. Why this root cause is supported by the evidence.
3. Which metrics/logs support the conclusion.
4. Whether the ML prediction is supported or contradicted.
5. Recommended production actions.
6. Priority of each action.

Look for relationships between signals.

Examples:

High CPU + high latency + 5xx
→ possible application/resource saturation.

Database timeouts + high latency
→ possible database problem.

Deployment changed + increased errors
→ possible deployment regression.

High restarts + application errors
→ possible application instability.

High network latency + packet loss
→ possible network issue.

Use actual evidence instead of assumptions.

==================================================
RECOMMENDED ACTIONS
==================================================

You are NOT restricted to a fixed list of action types.

Suggest whatever action(s) would actually resolve or
mitigate the root cause, based strictly on the evidence.

Examples of action_type values (not exhaustive — use
whatever best describes the real remediation step):

RESTART_APPLICATION
START_APPLICATION
STOP_APPLICATION
DEPLOY_APPLICATION
ROLLBACK_DEPLOYMENT
RESET_CREDENTIALS
ROTATE_SECRET
UPDATE_CONFIGURATION
SCALE_RESOURCES
NOTIFY_TEAM
ESCALATE_TO_ONCALL
INVESTIGATE_EXTERNAL_SERVICE

Use a short, clear, UPPER_SNAKE_CASE action_type that
accurately names the remediation step.

Only recommend an action when evidence supports it.

If there is not enough evidence for any action,
return an empty recommended_actions list.

Priority:

1 = highest
2 = medium
3 = lower

==================================================
OUTPUT
==================================================

Return ONLY this JSON structure:

{{
    "root_cause": "",

    "reasoning": "",

    "llm_confidence": 0,

    "recommended_actions": [
        {{
            "title": "",
            "action_type": "",
            "target": "",
            "priority": 1
        }}
    ]
}}

Rules:

- JSON only.
- No Markdown.
- No invented facts.
- No invented metrics.
- No invented logs.
- Evidence has priority over ML prediction.
- reasoning must reference actual evidence.
- llm_confidence must be between 0 and 100.
- Sort actions by priority.
"""