"""
Workflow State Models
Manages orchestration workflow state and status
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Types of agents in the system"""
    PLANNER = "planner"
    EXECUTOR = "executor"
    VALIDATOR = "validator"


class TaskStatus(str, Enum):
    """Individual task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    """Individual task in a workflow"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    agent_type: AgentType
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=1, ge=1, le=10)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowState(BaseModel):
    """Complete workflow state"""
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    tasks: List[Task] = Field(default_factory=list)
    current_task_index: int = 0
    context: Dict[str, Any] = Field(default_factory=dict, description="Shared workflow context")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_123456",
                "name": "Update Customer Profile",
                "description": "Update customer subscription and credit limit",
                "status": "running",
                "tasks": [
                    {
                        "task_id": "task_1",
                        "description": "Plan customer update",
                        "agent_type": "planner",
                        "status": "completed"
                    },
                    {
                        "task_id": "task_2",
                        "description": "Execute database update",
                        "agent_type": "executor",
                        "status": "in_progress"
                    }
                ],
                "current_task_index": 1,
                "context": {"customer_id": "CUST001"}
            }
        }


class WorkflowRequest(BaseModel):
    """Request to create a new workflow"""
    name: str
    description: Optional[str] = None
    operation: str = Field(..., description="Operation type: create, update, delete, query")
    target_customer_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Update Customer Subscription",
                "description": "Upgrade customer to Premium plan",
                "operation": "update",
                "target_customer_id": "CUST001",
                "parameters": {
                    "subscription_plan": "Premium",
                    "credit_limit": 100000
                }
            }
        }


class WorkflowResponse(BaseModel):
    """Response after workflow creation or status check"""
    workflow_id: str
    status: WorkflowStatus
    message: str
    current_task: Optional[Task] = None
    progress: float = Field(ge=0, le=100, description="Completion percentage")
