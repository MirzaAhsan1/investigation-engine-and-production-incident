from enum import Enum


class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class StatusEnum(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class IncidentSourceEnum(str, Enum):
    MANUAL = "MANUAL"
    API = "API"
    EMAIL = "EMAIL"
    SIEM = "SIEM"
    MONITORING = "MONITORING"
    AI = "AI"


class IncidentTypeEnum(str, Enum):
    SECURITY = "SECURITY"
    APPLICATION = "APPLICATION"
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    CLOUD = "CLOUD"
    ENDPOINT = "ENDPOINT"
    EMAIL = "EMAIL"
    OTHER = "OTHER"