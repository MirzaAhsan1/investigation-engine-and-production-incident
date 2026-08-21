from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class LogIngestRequest(BaseModel):

    api_key: str

    container_name: str

    host: str

    level: Optional[str] = None

    message: str

    timestamp: datetime


class LogIngestBatchRequest(BaseModel):

    logs: list[LogIngestRequest]