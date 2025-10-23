"""
Orchestration Engine
Manages workflow state and coordinates agent execution
This is a core reusable asset - the Orchestration Engine module
"""
from typing import Dict, Any, List, Optional
from app.models.workflow import (
    WorkflowState, WorkflowStatus, WorkflowRequest, WorkflowResponse,
    Task, TaskStatus, AgentType
)
from app.models.message import AgentMessage, MessageType
from app.agents import PlannerAgent, ExecutorAgent, ValidatorAgent
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
import asyncio


class OrchestrationEngine:
    """
    Core Orchestration Engine
    
    Responsibilities:
    - Start and manage workflows
    - Store and update workflow state (pending, running, completed)
    - Call agents in sequence
    - Coordinate inter-agent communication
    - Handle errors and retries
    """
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowState] = {}
        self.planner_agent = PlannerAgent()
        self.executor_agent = ExecutorAgent()
        self.validator_agent = ValidatorAgent()
        self.max_concurrent_workflows = 5
        self.log("Orchestration Engine initialized")
    
    def log(self, message: str):
        """Log orchestrator activity"""
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
                workflow_id=None,
                status=WorkflowStatus.FAILED,
                message=f"Maximum concurrent workflows ({self.max_concurrent_workflows}) reached",
                progress=0
            )
        
        # Create workflow state
        workflow = WorkflowState(
            name=request.name,
            description=request.description,
            context={
                "operation": request.operation,
                "target_customer_id": request.target_customer_id,
                "parameters": request.parameters
            }
        )
        
        self.workflows[workflow.workflow_id] = workflow
        # store and log immediately to ensure the workflow is discoverable by status queries
        self.log(f"Created workflow: {workflow.workflow_id} - {workflow.name}")
        self.log(f"Stored workflow in orchestrator state: {workflow.workflow_id}")
        
        # Generate task plan using Planner Agent
        await self._plan_workflow(workflow, db_session)
        
        # Start workflow execution in background with its own database session
        asyncio.create_task(self._execute_workflow_background(workflow))
        
        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            status=workflow.status,
            message=f"Workflow created and started",
            current_task=workflow.tasks[0] if workflow.tasks else None,
            progress=0
        )
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResponse]:
        """Get current status of a workflow"""
        workflow = self.workflows.get(workflow_id)
        
        if not workflow:
            return None
        
        # Calculate progress
        if not workflow.tasks:
            progress = 0
        else:
            completed_tasks = sum(
                1 for t in workflow.tasks 
                if t.status == TaskStatus.COMPLETED
            )
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
    
    async def _plan_workflow(self, workflow: WorkflowState, db_session: AsyncSession):
        """Use Planner Agent to generate task plan"""
        self.log(f"Planning workflow: {workflow.workflow_id}")
        
        workflow.status = WorkflowStatus.PENDING
        
        try:
            # Create message for planner
            message = AgentMessage(
                message_type=MessageType.REQUEST,
                sender_id="orchestrator",
                sender_type="orchestrator",
                receiver_id=self.planner_agent.agent_id,
                receiver_type="planner",
                workflow_id=workflow.workflow_id,
                action="plan_workflow",
                payload={
                    "operation": workflow.context["operation"],
                    "target_customer_id": workflow.context.get("target_customer_id"),
                    "parameters": workflow.context.get("parameters", {})
                }
            )
            
            # Get plan from planner agent
            response = await self.planner_agent.process_message(message)
            
            if not response.success:
                raise Exception(response.error)
            
            # Convert plan to tasks
            task_definitions = response.result.get("tasks", [])
            for task_def in task_definitions:
                task = Task(
                    task_id=task_def["task_id"],
                    description=task_def["description"],
                    agent_type=AgentType(task_def["agent_type"]),
                    status=TaskStatus.PENDING,
                    priority=task_def.get("priority", 1),
                    parameters=task_def.get("parameters", {})
                )
                workflow.tasks.append(task)
            
            self.log(f"Generated {len(workflow.tasks)} tasks for workflow {workflow.workflow_id}")
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            self.log(f"Failed to plan workflow: {str(e)}")
    
    async def _execute_workflow_background(self, workflow: WorkflowState):
        """Execute workflow in background with its own database session"""
        from app.database import AsyncSessionLocal
        
        # Create a new database session for this background task
        async with AsyncSessionLocal() as db_session:
            await self._execute_workflow(workflow, db_session)
    
    async def _execute_workflow(self, workflow: WorkflowState, db_session: AsyncSession):
        """Execute workflow tasks in sequence"""
        self.log(f"Starting workflow execution: {workflow.workflow_id}")
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        
        try:
            # Set database session for executor
            self.executor_agent.set_db_session(db_session)
            
            # Execute tasks in sequence
            for i, task in enumerate(workflow.tasks):
                workflow.current_task_index = i
                self.log(f"Executing task {i+1}/{len(workflow.tasks)}: {task.description}")
                
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.utcnow()
                
                try:
                    # Route task to appropriate agent
                    if task.agent_type == AgentType.PLANNER:
                        result = await self.planner_agent.execute_task({
                            "description": task.description,
                            "parameters": {**task.parameters, **workflow.context}
                        })
                    elif task.agent_type == AgentType.EXECUTOR:
                        result = await self.executor_agent.execute_task({
                            "description": task.description,
                            "parameters": {**task.parameters, **workflow.context}
                        })
                    elif task.agent_type == AgentType.VALIDATOR:
                        result = await self.validator_agent.execute_task({
                            "description": task.description,
                            "parameters": {**task.parameters, **workflow.context}
                        })
                    else:
                        # Unknown agent types are simulated
                        result = {"status": "success", "message": "Task simulated"}
                    
                    task.result = result

                    # If this is a validator pre-execution check and it failed, abort the workflow
                    try:
                        is_validator = task.agent_type == AgentType.VALIDATOR
                        validation_type = task.parameters.get("validation_type") if isinstance(task.parameters, dict) else None
                        valid_flag = None
                        if isinstance(result, dict):
                            # expected shape: {"status":..., "result": {"valid": bool, ...}}
                            valid_flag = result.get("result", {}).get("valid")

                        if is_validator and validation_type == "pre_execution" and valid_flag is False:
                            task.status = TaskStatus.FAILED
                            task.completed_at = datetime.utcnow()
                            task.error = "Pre-execution validation failed"
                            workflow.status = WorkflowStatus.FAILED
                            workflow.error = f"Validation failed: {result.get('result', {}).get('errors', [])}"
                            workflow.completed_at = datetime.utcnow()
                            self.log(f"Workflow {workflow.workflow_id} failed due to validation errors: {workflow.error}")
                            # stop executing further tasks
                            break

                    except Exception:
                        # if we can't parse validator result for some reason, continue as normal
                        pass

                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.utcnow()
                    
                    self.log(f"Task completed: {task.description}")
                    
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.completed_at = datetime.utcnow()
                    self.log(f"Task failed: {task.description} - {str(e)}")
                    raise e
            
            # All tasks completed successfully
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            self.log(f"Workflow completed: {workflow.workflow_id}")
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            workflow.completed_at = datetime.utcnow()
            self.log(f"Workflow failed: {workflow.workflow_id} - {str(e)}")
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows with their current status"""
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
