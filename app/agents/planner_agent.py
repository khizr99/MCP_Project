"""
Planner Agent
Generates task lists and plans for workflow execution
"""
from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent
from app.models.message import AgentMessage, MessageResponse, MessageType
from app.models.workflow import AgentType, Task, TaskStatus
import uuid


class PlannerAgent(BaseAgent):
    """
    Planner Agent - Analyzes requests and generates executable task lists
    
    Responsibilities:
    - Analyze incoming workflow requests
    - Generate detailed task plans
    - Validate request feasibility
    - Determine task sequence and dependencies
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(AgentType.PLANNER, agent_id)
        self.log("Planner Agent initialized")
    
    async def process_message(self, message: AgentMessage) -> MessageResponse:
        """Process incoming message and route to appropriate handler"""
        self.log(f"Processing message: {message.action}")
        
        try:
            if message.action == "plan_workflow":
                result = await self.plan_workflow(message.payload)
            elif message.action == "validate_request":
                result = await self.validate_request(message.payload)
            else:
                raise ValueError(f"Unknown action: {message.action}")
            
            return MessageResponse(
                success=True,
                message_id=message.message_id,
                result=result
            )
        except Exception as e:
            self.log(f"Error processing message: {str(e)}")
            return MessageResponse(
                success=False,
                message_id=message.message_id,
                error=str(e)
            )
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a planning task"""
        self.status = "busy"
        self.log(f"Executing task: {task.get('description')}")
        
        try:
            operation = task.get("parameters", {}).get("operation")
            
            if operation == "create":
                plan = await self._plan_create_customer(task["parameters"])
            elif operation == "update":
                plan = await self._plan_update_customer(task["parameters"])
            elif operation == "delete":
                plan = await self._plan_delete_customer(task["parameters"])
            elif operation == "query":
                plan = await self._plan_query_customer(task["parameters"])
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            self.status = "idle"
            return {
                "status": "success",
                "plan": plan,
                "message": f"Generated plan for {operation} operation"
            }
        except Exception as e:
            self.status = "idle"
            raise e
    
    async def plan_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete task plan for a workflow"""
        operation = payload.get("operation")
        parameters = payload.get("parameters", {})
        
        self.log(f"Planning workflow for operation: {operation}")
        
        tasks = []
        
        # Add pre-execution validation task (handled by ValidatorAgent)
        tasks.append({
            "task_id": str(uuid.uuid4()),
            "description": f"Validate {operation} request",
            "agent_type": "validator",
            "status": "pending",
            "priority": 1,
            "parameters": {
                "operation": operation,
                "validation_type": "pre_execution"
            }
        })
        
        # Add execution task
        tasks.append({
            "task_id": str(uuid.uuid4()),
            "description": f"Execute {operation} operation",
            "agent_type": "executor",
            "status": "pending",
            "priority": 2,
            "parameters": {
                "operation": operation,
                **parameters
            }
        })
        
        # Add post-validation task
        tasks.append({
            "task_id": str(uuid.uuid4()),
            "description": f"Validate {operation} result",
            "agent_type": "validator",
            "status": "pending",
            "priority": 3,
            "parameters": {
                "operation": operation,
                "validation_type": "post_execution"
            }
        })
        
        return {
            "tasks": tasks,
            "estimated_duration": len(tasks) * 5,  # 5 seconds per task
            "complexity": "medium"
        }
    
    async def validate_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if a request can be executed"""
        operation = payload.get("operation")
        parameters = payload.get("parameters", {})
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate based on operation type
        if operation == "update" and not parameters:
            validation_results["valid"] = False
            validation_results["errors"].append("Update operation requires parameters")
        
        if operation in ["update", "delete"] and not payload.get("target_customer_id"):
            validation_results["valid"] = False
            validation_results["errors"].append("Customer ID required for this operation")
        
        return validation_results
    
    async def _plan_create_customer(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate plan for customer creation"""
        return [
            {
                "step": 1,
                "action": "validate_customer_data",
                "description": "Validate customer information"
            },
            {
                "step": 2,
                "action": "check_duplicate",
                "description": "Check for duplicate customer"
            },
            {
                "step": 3,
                "action": "insert_customer",
                "description": "Insert new customer record"
            }
        ]
    
    async def _plan_update_customer(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate plan for customer update"""
        return [
            {
                "step": 1,
                "action": "fetch_current_data",
                "description": "Retrieve current customer data"
            },
            {
                "step": 2,
                "action": "validate_updates",
                "description": "Validate update parameters"
            },
            {
                "step": 3,
                "action": "apply_updates",
                "description": "Apply updates to customer record"
            }
        ]
    
    async def _plan_delete_customer(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate plan for customer deletion"""
        return [
            {
                "step": 1,
                "action": "verify_customer_exists",
                "description": "Verify customer exists"
            },
            {
                "step": 2,
                "action": "check_dependencies",
                "description": "Check for dependent records"
            },
            {
                "step": 3,
                "action": "delete_customer",
                "description": "Delete customer record"
            }
        ]
    
    async def _plan_query_customer(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate plan for customer query"""
        return [
            {
                "step": 1,
                "action": "build_query",
                "description": "Build database query"
            },
            {
                "step": 2,
                "action": "execute_query",
                "description": "Execute query and retrieve data"
            },
            {
                "step": 3,
                "action": "format_results",
                "description": "Format and return results"
            }
        ]
