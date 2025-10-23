# MCP_Project/app/agents/base_agent.py

"""
Base Agent Class
Abstract base class for all agents in the system
With context-aware ACL support
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.models.message import AgentMessage, MessageType, MessageResponse, ContextData
from app.models.workflow import AgentType
from app.memory.context_store import ContextStore
import uuid
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Provides common functionality and enforces interface.
    Integrates context-awareness via ContextStore.
    """

    def __init__(self, agent_type: AgentType, context_store: ContextStore, agent_id: Optional[str] = None):
        self.agent_id = agent_id or f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.status = "idle"
        self.message_history = []
        self.context_store = context_store  # Reference to central memory

    @abstractmethod
    async def process_message(self, message: AgentMessage) -> MessageResponse:
        """
        Process an incoming message and return a response.
        Must be implemented by all agents.
        """
        pass

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task.
        Must be implemented by all agents.
        """
        pass

    def create_message(
        self,
        message_type: MessageType,
        receiver_id: str,
        receiver_type: str,
        workflow_id: str,
        action: str,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Create a standardized, context-aware message.
        Automatically attaches current workflow context.
        """
        # Fetch current workflow context
        workflow_context = self.context_store.get_context(workflow_id)
        context_data = ContextData(
            previous_actions=workflow_context.get("previous_actions", []),
            metadata={**workflow_context.get("metadata", {}), **(metadata or {})},
            last_updated=datetime.utcnow()
        )

        # Create message
        message = AgentMessage(
            message_type=message_type,
            sender_id=self.agent_id,
            sender_type=self.agent_type.value,
            receiver_id=receiver_id,
            receiver_type=receiver_type,
            workflow_id=workflow_id,
            task_id=task_id,
            action=action,
            payload=payload,
            in_reply_to=in_reply_to,
            context=context_data,
            metadata=metadata or {}
        )

        # Update context with this action
        self.context_store.update_context(workflow_id, action=action, metadata=metadata)

        # Save message history
        self.message_history.append(message)

        return message

    def log(self, message: str):
        """Log agent activity"""
        timestamp = datetime.utcnow().isoformat()
        print(f"[{timestamp}] [{self.agent_type.value}:{self.agent_id}] {message}")
