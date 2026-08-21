from enum import Enum


class LogStatusEnum(str, Enum):

    PENDING = "PENDING"

    PROCESSING = "PROCESSING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    IGNORED = "IGNORED"