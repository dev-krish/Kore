from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import Field
from app.models.common import BaseDBModel

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class ToolCallRecord(BaseDBModel):
    toolName: str
    inputArgs: Dict[str, Any]
    outputSummary: Optional[str] = None
    isSuccess: bool = True
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentStepRecord(BaseDBModel):
    stepNumber: int
    task: str
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    status: str = "completed"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentExecutionModel(BaseDBModel):
    id: Optional[str] = Field(default=None, alias="_id")
    campaignId: str
    userId: str
    currentStep: int = 0
    totalSteps: int = 0
    executionStatus: ExecutionStatus = ExecutionStatus.PENDING
    planTasks: List[str] = []
    toolCalls: List[ToolCallRecord] = []
    steps: List[AgentStepRecord] = []
    errors: List[str] = []
    summary: Optional[str] = None
    startedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completedAt: Optional[datetime] = None
