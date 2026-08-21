from app.models.enums import (
    SeverityEnum,
    IncidentSourceEnum,
    IncidentTypeEnum,
)


SEVERITY_SCORES = {
    SeverityEnum.LOW: 10,
    SeverityEnum.MEDIUM: 30,
    SeverityEnum.HIGH: 60,
    SeverityEnum.CRITICAL: 90,
}


TYPE_SCORES = {
    IncidentTypeEnum.SECURITY: 20,
    IncidentTypeEnum.DATABASE: 15,
    IncidentTypeEnum.NETWORK: 15,
    IncidentTypeEnum.CLOUD: 15,
    IncidentTypeEnum.APPLICATION: 10,
    IncidentTypeEnum.ENDPOINT: 10,
    IncidentTypeEnum.EMAIL: 5,
    IncidentTypeEnum.OTHER: 5,
}


SOURCE_SCORES = {
    IncidentSourceEnum.SIEM: 15,
    IncidentSourceEnum.AI: 15,
    IncidentSourceEnum.MONITORING: 10,
    IncidentSourceEnum.API: 5,
    IncidentSourceEnum.EMAIL: 5,
    IncidentSourceEnum.MANUAL: 0,
}

SAFE_THRESHOLD = 30
MEDIUM_THRESHOLD = 60
HIGH_THRESHOLD = 80
MAX_SCORE = 100
# risk_score = min(total_score, MAX_SCORE)