# MCP_Project/app/agents/planner_agent.py

from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent
from app.models.message import AgentMessage, MessageResponse
from app.models.workflow import AgentType
from app.memory.context_store import ContextStore
import uuid


class PlannerAgent(BaseAgent):
    """
    Planner Agent - Analyzes requests and generates executable task lists.
    Passes all parameters including target_customer_id to ExecutorAgent.
    """

    def __init__(self, context_store: ContextStore, agent_id: Optional[str] = None):
        super().__init__(AgentType.PLANNER, context_store, agent_id)
        self.log("Planner Agent initialized")

    async def process_message(self, message: AgentMessage) -> MessageResponse:
        """Handle ACL messages and route to appropriate planner methods"""
        self.log(f"Processing message: {message.action}")

        # Update workflow context
        if message.context:
            self.context_store.update_context(message.workflow_id, metadata=message.context.metadata)

        try:
            if message.action == "plan_workflow":
                result = await self.plan_workflow(message.payload, message.workflow_id)
            elif message.action == "validate_request":
                result = await self.validate_request(message.payload, message.workflow_id)
            else:
                raise ValueError(f"Unknown action: {message.action}")

            return MessageResponse(
                success=True,
                message_id=message.message_id,
                result=result
            )
        except Exception as e:
            self.log(f"Error processing message: {str(e)}")
            return MessageResponse(success=False, message_id=message.message_id, error=str(e))

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate execution of a planning task"""
        self.status = "busy"
        self.log(f"Executing task: {task.get('description')}")

        try:
            operation = task.get("parameters", {}).get("operation") or task.get("operation")
            workflow_id = task.get("workflow_id")

            if not operation:
                raise ValueError("Missing 'operation' in task payload")

            # Route to specific planner method
            if operation == "create":
                plan = await self._plan_create_customer(task.get("parameters", {}))
            elif operation == "update":
                plan = await self._plan_update_customer(task.get("parameters", {}))
            elif operation == "delete":
                plan = await self._plan_delete_customer(task.get("parameters", {}))
            elif operation == "query":
                plan = await self._plan_query_customer(task.get("parameters", {}))
            else:
                raise ValueError(f"Unknown operation: {operation}")

            # Update workflow context with planning result
            if workflow_id:
                self.context_store.update_context(
                    workflow_id,
                    action=f"execute_{operation}_task",
                    metadata={"task_id": task.get("task_id"), "plan": plan}
                )

            return {"status": "success", "plan": plan, "message": f"Generated plan for {operation}"}
        finally:
            self.status = "idle"

    async def plan_workflow(self, payload: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Generate a list of tasks for the workflow based on operation"""
        operation = payload.get("operation")
        parameters = payload.get("parameters", {})

        if not operation:
            raise ValueError("Missing 'operation' in workflow payload")

        self.log(f"Planning workflow for operation: {operation}")

        tasks = []

        # Pre-execution validation task
        tasks.append({
            "task_id": str(uuid.uuid4()),
            "description": f"Validate {operation} request",
            "agent_type": "planner",
            "status": "pending",
            "priority": 1,
            "parameters": {"operation": operation, "validation_type": "pre_execution"},
            "workflow_id": workflow_id
        })

        # Execution task: passes target_customer_id and all parameters to Executor
        tasks.append({
            "task_id": str(uuid.uuid4()),
            "description": f"Execute {operation} operation",
            "agent_type": "executor",
            "status": "pending",
            "priority": 2,
            "parameters": {
                "operation": operation,
                "target_customer_id": payload.get("target_customer_id"),
                **parameters
            },
            "workflow_id": workflow_id
        })

        # Post-execution validation task
        tasks.append({
            "task_id": str(uuid.uuid4()),
            "description": f"Validate {operation} result",
            "agent_type": "validator",
            "status": "pending",
            "priority": 3,
            "parameters": {"operation": operation, "validation_type": "post_execution"},
            "workflow_id": workflow_id
        })

        # Update workflow context
        self.context_store.update_context(
            workflow_id,
            action=f"plan_{operation}_workflow",
            metadata={"task_count": len(tasks)}
        )

        return {"tasks": tasks, "estimated_duration": len(tasks) * 5, "complexity": "medium"}

    async def validate_request(self, payload: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Validate workflow payload before execution"""
        operation = payload.get("operation")
        parameters = payload.get("parameters", {})

        validation_results = {"valid": True, "errors": [], "warnings": []}

        if operation == "update" and not parameters:
            validation_results["valid"] = False
            validation_results["errors"].append("Update operation requires parameters")

        if operation in ["update", "delete"] and not payload.get("target_customer_id"):
            validation_results["valid"] = False
            validation_results["errors"].append("Customer ID required for this operation")

        # Log validation in workflow context
        self.context_store.update_context(
            workflow_id,
            action=f"validate_{operation}_request",
            metadata={"validation": validation_results}
        )

        return validation_results

    # ----------------------------
    # Private planner methods
    # ----------------------------
    async def _plan_create_customer(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "action": "validate_customer_data", "description": "Validate customer information"},
            {"step": 2, "action": "check_duplicate", "description": "Check for duplicate customer"},
            {"step": 3, "action": "insert_customer", "description": "Insert new customer record"}
        ]

    async def _plan_update_customer(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "action": "fetch_current_data", "description": "Retrieve current customer data"},
            {"step": 2, "action": "validate_updates", "description": "Validate update parameters"},
            {"step": 3, "action": "apply_updates", "description": "Apply updates to customer record"}
        ]

    async def _plan_delete_customer(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "action": "verify_customer_exists", "description": "Verify customer exists"},
            {"step": 2, "action": "check_dependencies", "description": "Check for dependent records"},
            {"step": 3, "action": "delete_customer", "description": "Delete customer record"}
        ]

    async def _plan_query_customer(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "action": "build_query", "description": "Build database query"},
            {"step": 2, "action": "execute_query", "description": "Execute query and retrieve data"},
            {"step": 3, "action": "format_results", "description": "Format and return results"}
        ]
