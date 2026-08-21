from app.models.incident import Incident
from app.models.evidence import Evidence


def generate_reasoning(
    incident: Incident,
    evidence: Evidence,
    prediction: dict,
) -> str:

    reasons = []

    reasons.append(
        f"The ML model classified this incident as '{prediction['predicted_category']}' with {prediction['confidence']}% confidence."
    )

    # CPU
    if evidence.cpu_usage >= 90:
        reasons.append(
            f"CPU usage is critically high ({evidence.cpu_usage}%)."
        )

    # Memory
    if evidence.memory_usage >= 90:
        reasons.append(
            f"Memory usage is critically high ({evidence.memory_usage}%)."
        )

    # Disk
    if evidence.disk_usage >= 90:
        reasons.append(
            f"Disk usage is almost full ({evidence.disk_usage}%)."
        )

    # API Latency
    if evidence.api_latency >= 3000:
        reasons.append(
            f"API latency is unusually high ({evidence.api_latency} ms)."
        )

    # Error Rate
    if evidence.error_rate >= 10:
        reasons.append(
            f"Application error rate is elevated ({evidence.error_rate}%)."
        )

    # DB Connections
    if evidence.db_connections >= 400:
        reasons.append(
            f"Database connection usage is extremely high ({evidence.db_connections})."
        )

    # Containers
    if evidence.active_containers <= 1:
        reasons.append(
            "Very few application containers are running."
        )

    # Logs
    if evidence.logs:
        reasons.append(
            f"Observed log message: {evidence.logs}"
        )

    reasons.append(
        "The above evidence indicates the most probable root cause identified by the ML model."
    )

    return " ".join(reasons)


def generate_recommendations(
    incident: Incident,
    prediction: dict,
) -> str:

    actions = []

    category = prediction["predicted_category"]

    if category == "DATABASE":

        actions.extend(
            [
                "Check database availability.",
                "Inspect active database connections.",
                "Review slow queries.",
                "Restart the database service if necessary.",
            ]
        )

    elif category == "APPLICATION":

        actions.extend(
            [
                "Inspect application logs.",
                "Review the latest deployment.",
                "Restart the affected application service.",
            ]
        )

    elif category == "NETWORK":

        actions.extend(
            [
                "Verify network connectivity.",
                "Inspect firewall configuration.",
                "Check load balancer health.",
            ]
        )

    elif category == "CLOUD":

        actions.extend(
            [
                "Review cloud infrastructure health.",
                "Check cloud service status.",
                "Verify autoscaling events.",
            ]
        )

    elif category == "SECURITY":

        actions.extend(
            [
                "Review authentication logs.",
                "Inspect suspicious user activity.",
                "Check IDS/SIEM alerts.",
            ]
        )

    elif category == "EMAIL":

        actions.extend(
            [
                "Inspect mail server logs.",
                "Verify SMTP connectivity.",
            ]
        )

    elif category == "ENDPOINT":

        actions.extend(
            [
                "Verify endpoint health.",
                "Inspect endpoint security software.",
            ]
        )

    else:

        actions.append(
            "Perform manual investigation."
        )

    actions.append(
        "Validate the findings before applying changes."
    )

    actions.append(
        "Document the investigation results."
    )

    return " ".join(actions)