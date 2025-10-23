# MCP_Project/app/memory/context_store.py

from typing import Dict, Any, List
from threading import Lock
import uuid
from datetime import datetime

class ContextStore:
    """
    A thread-safe in-memory context store for agents.
    Stores context per agent or per workflow.
    """

    def __init__(self):
        self.store: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()

    def create_workflow_context(self) -> str:
        """Create a new workflow context ID"""
        workflow_id = str(uuid.uuid4())
        with self.lock:
            self.store[workflow_id] = {
                "created_at": datetime.utcnow(),
                "previous_actions": [],
                "metadata": {}
            }
        return workflow_id

    def get_context(self, workflow_id: str) -> Dict[str, Any]:
        """Retrieve context for a given workflow"""
        with self.lock:
            return self.store.get(workflow_id, {
                "previous_actions": [],
                "metadata": {}
            })

    def update_context(
        self,
        workflow_id: str,
        action: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Update context with a new action or metadata"""
        with self.lock:
            if workflow_id not in self.store:
                self.store[workflow_id] = {
                    "created_at": datetime.utcnow(),
                    "previous_actions": [],
                    "metadata": {}
                }
            if action:
                self.store[workflow_id]["previous_actions"].append(action)
            if metadata:
                self.store[workflow_id]["metadata"].update(metadata)

    def reset_context(self, workflow_id: str):
        """Reset a workflow's context"""
        with self.lock:
            if workflow_id in self.store:
                self.store[workflow_id] = {
                    "created_at": datetime.utcnow(),
                    "previous_actions": [],
                    "metadata": {}
                }

    def list_workflows(self) -> List[str]:
        """Return all workflow IDs"""
        with self.lock:
            return list(self.store.keys())
