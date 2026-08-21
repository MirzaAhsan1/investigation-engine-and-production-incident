from app.models.evidence import Evidence
from app.models.incident import Incident
from app.models.investigation import Investigation


def build_report(
    incident: Incident,
    evidence: Evidence,
    investigation: Investigation,
):

    return {

        # ====================================
        # Incident Information
        # ====================================

        "incident": {

            "id": str(incident.id),

            "title": incident.title,

            "description": incident.description,

            "severity": incident.severity.value,

            "status": incident.status.value,

            "type": incident.incident_type.value,

            "source": incident.source.value,

            "created_at": incident.created_at,

        },

        # ====================================
        # Infrastructure Evidence
        # ====================================

        "evidence": {

            "service_name": evidence.service_name,

            "environment": evidence.environment,

            "deployment_changed": evidence.deployment_changed,

            "cpu_usage": evidence.cpu_usage,

            "memory_usage": evidence.memory_usage,

            "disk_usage": evidence.disk_usage,

            "disk_io_wait": evidence.disk_io_wait,

            "api_latency": evidence.api_latency,

            "network_latency": evidence.network_latency,

            "packet_loss": evidence.packet_loss,

            "error_rate": evidence.error_rate,

            "db_connections": evidence.db_connections,

            "database_timeout_count": evidence.database_timeout_count,

            "active_containers": evidence.active_containers,

            "restart_count": evidence.restart_count,

            "pod_restart_count": evidence.pod_restart_count,

            "request_per_second": evidence.request_per_second,

            "http_5xx_count": evidence.http_5xx_count,

            "http_4xx_count": evidence.http_4xx_count,

            "failed_login_attempts": evidence.failed_login_attempts,

            "ssl_certificate_days_left": evidence.ssl_certificate_days_left,

            "logs": evidence.logs,

        },

        # ====================================
        # Machine Learning Result
        # ====================================

        "ml_prediction": {

            "predicted_category": investigation.predicted_category,

            "predicted_cause": investigation.predicted_cause,

            "confidence": investigation.confidence,

            "risk_score": investigation.risk_score,

        },

        # ====================================
        # AI Investigation
        # ====================================

        "ai_analysis": {

            "root_cause": investigation.root_cause,

            "reasoning": investigation.reasoning,

            "llm_confidence": investigation.llm_confidence,

        },

        # ====================================
        # Rule Engine
        # ====================================

        "triggered_rules": investigation.triggered_rules,

        # ====================================
        # Recommendations
        # ====================================

        "recommended_actions": investigation.recommended_actions,

        # ====================================
        # Action Queue
        # ====================================

        "action_queue": [

            {

                "id": str(action.id),

                "title": action.title,

                "action_type": action.action_type,

                "target": action.target,

                "priority": action.priority,

                "status": action.status.value,

                "created_at": action.created_at,

            }

            for action in investigation.actions

        ],

        # ====================================
        # Investigation Status
        # ====================================

        "analysis": {

            "status": investigation.analysis_status.value,

            "created_at": investigation.created_at,

            "updated_at": investigation.updated_at,

        },

    }