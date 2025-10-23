# MCP_Project/app/agents/executor_agent.py

from app.agents.base_agent import BaseAgent
from app.models.message import AgentMessage, MessageResponse
from app.models.workflow import AgentType
from app.memory.context_store import ContextStore
from app.database import CustomerDB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect
from datetime import datetime
import json

class ExecutorAgent(BaseAgent):
    """Executor agent that dynamically updates customer records"""

    def __init__(self, context_store: ContextStore, agent_id: str = None):
        super().__init__(AgentType.EXECUTOR, context_store, agent_id)
        self.db_session: AsyncSession = None
        self.log("Executor Agent initialized")

    def set_db_session(self, db_session: AsyncSession):
        """Set the database session to use"""
        self.db_session = db_session

    async def process_message(self, message: AgentMessage) -> MessageResponse:
        """Process an ACL message"""
        self.log(f"Processing message: {message.action}")
        workflow_id = message.workflow_id

        # Update context if provided
        if message.context:
            self.context_store.update_context(workflow_id, metadata=message.context.metadata)

        try:
            result = await self.execute_task(message.payload or {}, workflow_id)
            return MessageResponse(
                success=True,
                message_id=message.message_id,
                result=result
            )
        except Exception as e:
            self.log(f"Error executing task: {str(e)}")
            return MessageResponse(
                success=False,
                message_id=message.message_id,
                error=str(e)
            )

    async def execute_task(self, payload: dict, workflow_id: str):
        """Execute a workflow task and update customer dynamically"""

        self.status = "busy"
        try:
            # Get target customer
            target_customer_id = payload.get("target_customer_id")
            if not target_customer_id:
                raise ValueError("target_customer_id missing in payload")

            customer = await self.db_session.get(CustomerDB, target_customer_id)
            if not customer:
                raise ValueError(f"Customer {target_customer_id} not found")

            # Get list of all column names in CustomerDB
            mapper = inspect(CustomerDB)
            allowed_fields = [c.key for c in mapper.columns if c.key != "mcp_id"]

            updated_fields = []

            for field in allowed_fields:
                if field in payload:
                    value = payload[field]
                    # Handle JSON column
                    if mapper.columns[field].type.python_type == dict:
                        if isinstance(value, str):
                            try:
                                value = json.loads(value)
                            except:
                                value = {"raw": value}
                    # Handle int/float conversions
                    elif mapper.columns[field].type.python_type == int:
                        value = int(value)
                    elif mapper.columns[field].type.python_type == float:
                        value = float(value)
                    # Update attribute
                    setattr(customer, field, value)
                    updated_fields.append(field)

            customer.updated_at = datetime.utcnow()

            # Commit changes
            self.db_session.add(customer)
            await self.db_session.commit()

            # Update context store
            self.context_store.update_context(
                workflow_id,
                action=f"executed_update_{target_customer_id}",
                metadata={"updated_fields": updated_fields}
            )

            self.log(f"Customer {target_customer_id} updated: {updated_fields}")

            return {"status": "success", "customer_id": target_customer_id, "updated_fields": updated_fields}

        except Exception as e:
            self.context_store.update_context(
                workflow_id,
                action=f"failed_update_{payload.get('target_customer_id', 'unknown')}",
                metadata={"error": str(e)}
            )
            raise e
        finally:
            self.status = "idle"
