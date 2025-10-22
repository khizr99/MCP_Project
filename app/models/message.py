"""
Agent Communication Protocol (ACL)
Standard JSON format for inter-agent communication
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class MessageType(str, Enum):
    """Types of messages agents can send"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    ACKNOWLEDGEMENT = "ack"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentMessage(BaseModel):
    """
    Standard Agent Communication Protocol (ACL) Message Format
    
    This is the core reusable asset - a standardized JSON format
    for all inter-agent communication in the system.
    """
    # Message Metadata
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = Field(..., description="Type of message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: MessagePriority = MessagePriority.MEDIUM
    
    # Sender Information
    sender_id: str = Field(..., description="ID of the sending agent")
    sender_type: str = Field(..., description="Type of sending agent (planner, executor, etc.)")
    
    # Receiver Information
    receiver_id: Optional[str] = Field(default=None, description="ID of target agent (None for broadcast)")
    receiver_type: Optional[str] = Field(default=None, description="Type of target agent")
    
    # Workflow Context
    workflow_id: str = Field(..., description="Associated workflow ID")
    task_id: Optional[str] = Field(default=None, description="Associated task ID")
    
    # Message Content
    action: str = Field(..., description="Action to be performed")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message data/parameters")
    
    # Response/Error Handling
    in_reply_to: Optional[str] = Field(default=None, description="Message ID this is replying to")
    status: str = Field(default="pending", description="Message processing status")
    error: Optional[str] = Field(default=None, description="Error message if any")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_123456",
                "message_type": "request",
                "timestamp": "2024-01-15T10:30:00",
                "priority": "high",
                "sender_id": "orchestrator_1",
                "sender_type": "orchestrator",
                "receiver_id": "planner_1",
                "receiver_type": "planner",
                "workflow_id": "wf_123",
                "task_id": "task_1",
                "action": "plan_update",
                "payload": {
                    "customer_id": "CUST001",
                    "operation": "update",
                    "fields": {"subscription_plan": "Premium"}
                },
                "status": "pending"
            }
        }


class MessageBatch(BaseModel):
    """Batch of messages for bulk operations"""
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[AgentMessage]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageResponse(BaseModel):
    """Standard response to a message"""
    success: bool
    message_id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
