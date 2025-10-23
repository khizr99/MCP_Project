"""
Validator Agent
Performs pre- and post-execution validation for workflows and tasks
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.models.message import AgentMessage, MessageResponse
from app.models.workflow import AgentType


class ValidatorAgent(BaseAgent):
    """
    Validator Agent - validates requests and results.

    Responsibilities:
    - Run pre-execution validations (required fields, parameter sanity)
    - Run post-execution validations (result checks, consistency)
    - Return structured validation results
    """

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(AgentType.VALIDATOR, agent_id)
        self.log("Validator Agent initialized")

    async def process_message(self, message: AgentMessage) -> MessageResponse:
        self.log(f"Processing message: {message.action}")

        try:
            if message.action == "validate_request":
                result = await self._validate_request(message.payload)
            elif message.action == "validate_result":
                result = await self._validate_result(message.payload)
            else:
                raise ValueError(f"Unknown action: {message.action}")

            return MessageResponse(success=True, message_id=message.message_id, result=result)
        except Exception as e:
            self.log(f"Error processing message: {str(e)}")
            return MessageResponse(success=False, message_id=message.message_id, error=str(e))

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.status = "busy"
        self.log(f"Executing validation task: {task.get('description')}")

        try:
            params = task.get("parameters", {})
            validation_type = params.get("validation_type") or params.get("type")

            if validation_type == "pre_execution":
                result = await self._validate_request({**task.get('parameters', {}), **params})
            elif validation_type == "post_execution":
                result = await self._validate_result({**task.get('parameters', {}), **params})
            else:
                # default to a light-weight validation
                result = {"valid": True, "errors": [], "warnings": []}

            self.status = "idle"
            return {"status": "success", "result": result}
        except Exception as e:
            self.status = "idle"
            raise e

    async def _validate_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform pre-execution validation on the incoming request payload"""
        operation = payload.get("operation")
        parameters = payload.get("parameters", {})
        target_customer_id = payload.get("target_customer_id") or payload.get("customer_id")

        validation_results = {"valid": True, "errors": [], "warnings": []}

        if operation in ["update", "delete"] and not target_customer_id:
            validation_results["valid"] = False
            validation_results["errors"].append("Missing target_customer_id for update/delete operation")

        if operation == "update" and not parameters:
            validation_results["valid"] = False
            validation_results["errors"].append("Update operation requires parameters")

        # Basic sanity checks
        if parameters.get("credit_limit") is not None:
            try:
                cl = float(parameters.get("credit_limit"))
                if cl < 0:
                    validation_results["valid"] = False
                    validation_results["errors"].append("credit_limit cannot be negative")
            except Exception:
                validation_results["valid"] = False
                validation_results["errors"].append("credit_limit must be a number")

        return validation_results

    async def _validate_result(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform post-execution validation on the result of the operation"""
        # Basic post-check: ensure the execution reported success
        result = payload.get("result") or {}
        validation_results = {"valid": True, "errors": [], "warnings": []}

        if isinstance(result, dict) and result.get("success") is False:
            validation_results["valid"] = False
            validation_results["errors"].append(result.get("error") or "Execution reported failure")

        # Otherwise, accept as valid
        return validation_results
