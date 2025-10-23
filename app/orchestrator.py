# MCP_Project/app/orchestrator.py

from typing import Dict, Any, List, Optional
from app.models.workflow import (
    WorkflowState, WorkflowStatus, WorkflowRequest, WorkflowResponse,
    Task, TaskStatus, AgentType
)
from app.agents.planner_agent import PlannerAgent
from app.agents.executor_agent import ExecutorAgent
from app.models.message import AgentMessage, MessageType
from app.memory.context_store import ContextStore
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
import asyncio


class OrchestrationEngine:
    """Core Orchestration Engine for workflow execution"""

    def __init__(self):
        self.workflows: Dict[str, WorkflowState] = {}
        self.context_store = ContextStore()
        self.planner_agent = PlannerAgent(context_store=self.context_store)
        self.executor_agent = ExecutorAgent(context_store=self.context_store)
        self.max_concurrent_workflows = 5
        self.log("Orchestration Engine initialized")

    def log(self, message: str):
        timestamp = datetime.utcnow().isoformat()
        print(f"[{timestamp}] [ORCHESTRATOR] {message}")

    async def create_workflow(
        self,
        request: WorkflowRequest,
        db_session: AsyncSession
    ) -> WorkflowResponse:
        """Create and start a new workflow"""

        # Check concurrent workflow limit
        active_workflows = sum(
            1 for w in self.workflows.values()
            if w.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]
        )
        if active_workflows >= self.max_concurrent_workflows:
            return WorkflowResponse(
                workflow_id="",
                status=WorkflowStatus.FAILED,
                message="Maximum concurrent workflows reached",
                progress=0
            )

        # Create workflow state
        workflow = WorkflowState(
            name=request.name,
            description=request.description,
            context={
                "operation": request.operation,
                "target_customer_id": request.target_customer_id,
                "parameters": request.parameters or {}
            }
        )
        self.workflows[workflow.workflow_id] = workflow
        self.log(f"Created workflow: {workflow.workflow_id} - {workflow.name}")

        # Plan workflow tasks
        await self._plan_workflow(workflow)

        # Execute workflow in background
        asyncio.create_task(self._execute_workflow_background(workflow))

        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            status=workflow.status,
            message="Workflow created and started",
            current_task=workflow.tasks[0] if workflow.tasks else None,
            progress=0
        )

    async def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResponse]:
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None

        if not workflow.tasks:
            progress = 0
        else:
            completed_tasks = sum(1 for t in workflow.tasks if t.status == TaskStatus.COMPLETED)
            progress = (completed_tasks / len(workflow.tasks)) * 100

        current_task = None
        if workflow.current_task_index < len(workflow.tasks):
            current_task = workflow.tasks[workflow.current_task_index]

        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            status=workflow.status,
            message=f"Workflow {workflow.status.value}",
            current_task=current_task,
            progress=progress
        )

    async def _plan_workflow(self, workflow: WorkflowState):
        """Generate workflow tasks using PlannerAgent"""
        self.log(f"Planning workflow: {workflow.workflow_id}")
        workflow.status = WorkflowStatus.PENDING

        try:
            message = self.planner_agent.create_message(
                message_type=MessageType.REQUEST,
                receiver_id=self.planner_agent.agent_id,
                receiver_type="planner",
                workflow_id=workflow.workflow_id,
                action="plan_workflow",
                payload={
                    "operation": workflow.context.get("operation"),
                    "target_customer_id": workflow.context.get("target_customer_id"),
                    "parameters": workflow.context.get("parameters", {})
                }
            )

            response = await self.planner_agent.process_message(message)
            if not response.success:
                raise Exception(response.error)

            # Convert planned tasks into workflow tasks
            task_definitions = response.result.get("tasks", [])
            for task_def in task_definitions:
                task = Task(
                    task_id=task_def["task_id"],
                    description=task_def["description"],
                    agent_type=AgentType(task_def["agent_type"]),
                    status=TaskStatus.PENDING,
                    priority=task_def.get("priority", 1),
                    parameters=task_def.get("parameters", {}),
                )
                workflow.tasks.append(task)

            self.log(f"Generated {len(workflow.tasks)} tasks for workflow {workflow.workflow_id}")
            self.context_store.update_context(
                workflow.workflow_id,
                action="workflow_planned",
                metadata={"task_count": len(workflow.tasks)}
            )
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            self.log(f"Failed to plan workflow: {str(e)}")

    async def _execute_workflow_background(self, workflow: WorkflowState):
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db_session:
            await self._execute_workflow(workflow, db_session)

    async def _execute_workflow(self, workflow: WorkflowState, db_session: AsyncSession):
        self.log(f"Starting workflow execution: {workflow.workflow_id}")
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        try:
            self.executor_agent.set_db_session(db_session)
            for i, task in enumerate(workflow.tasks):
                workflow.current_task_index = i
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.utcnow()

                # Merge workflow context parameters into task
                agent_payload = {**task.parameters}
                workflow_params = workflow.context.get("parameters", {})
                if workflow_params:
                    agent_payload.update(workflow_params)
                if "operation" not in agent_payload:
                    agent_payload["operation"] = workflow.context.get("operation")
                if "target_customer_id" not in agent_payload:
                    agent_payload["target_customer_id"] = workflow.context.get("target_customer_id")
                agent_payload["description"] = task.description

                try:
                    if task.agent_type == AgentType.PLANNER:
                        result = await self.planner_agent.execute_task(agent_payload)
                    elif task.agent_type == AgentType.EXECUTOR:
                        result = await self.executor_agent.execute_task(agent_payload, workflow.workflow_id)
                    else:
                        result = {"status": "success", "message": "Task simulated"}

                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.utcnow()
                    self.context_store.update_context(
                        workflow.workflow_id,
                        action=f"executed_task_{task.task_id}",
                        metadata={"task_result": result}
                    )
                    self.log(f"Task completed: {task.description}")
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.completed_at = datetime.utcnow()
                    self.context_store.update_context(
                        workflow.workflow_id,
                        action=f"failed_task_{task.task_id}",
                        metadata={"error": str(e)}
                    )
                    self.log(f"Task failed: {task.description} - {str(e)}")
                    raise e

            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            self.log(f"Workflow completed: {workflow.workflow_id}")
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            workflow.completed_at = datetime.utcnow()
            self.log(f"Workflow failed: {workflow.workflow_id} - {str(e)}")

    def list_workflows(self) -> List[Dict[str, Any]]:
        return [
            {
                "workflow_id": w.workflow_id,
                "name": w.name,
                "status": w.status.value,
                "created_at": w.created_at.isoformat(),
                "tasks_total": len(w.tasks),
                "tasks_completed": sum(1 for t in w.tasks if t.status == TaskStatus.COMPLETED)
            }
            for w in self.workflows.values()
        ]


# Global orchestrator instance
orchestrator = OrchestrationEngine()
