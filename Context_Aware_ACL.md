File: app/memory/context_store.py

Overview

The ContextStore acts as a Context-Aware Access Control Layer for the MCP Multi-Agent Orchestration system. It provides real-time tracking of workflow execution, recording actions, task results, and updated fields.

It allows agents (Planner or Executor) to make context-aware decisions and enables APIs to report workflow status and updates without querying the database repeatedly.

Structure & Fields
1. created_at

Type: datetime

Description: Timestamp when the workflow context was first created.

Use: Helps track workflow start time.

2. previous_actions

Type: List[str]

Description: Chronological list of executed actions in the workflow.

Example:

["plan_workflow", "executed_task_1234", "executed_update_CUST001"]

3. actions

Type: List[Dict]

Description: Stores metadata for each action/task executed.

Example structure:

{
    "action": "executed_update_CUST001",
    "agent": "executor",
    "timestamp": "2025-10-23T14:05:38",
    "updated_fields": ["credit_limit", "subscription_plan"],
    "task_result": {"status": "success", "message": "Customer updated"}
}

4. metadata

Type: Dict

Description: Aggregated workflow info including:

task_count: Total tasks in workflow

updated_fields: Fields updated so far

task_result: Last task execution result

Purpose

Audit & Monitoring

Tracks who did what and when in the workflow.

Debugging

Full workflow execution history enables quick identification of failures.

Dynamic Agent Decisions

Agents can inspect previous actions/results to decide next steps.

API Reporting

Enables endpoints to show workflow progress and updated fields.

API Access

The context store can be inspected through two FastAPI endpoints:

1. Get workflow context by ID

Endpoint:

GET /api/workflows/{workflow_id}/context


Description:
Returns the full context for a specific workflow, including all actions and metadata.

Example Response:

{
  "workflow_id": "4d763c90-96ce-4365-aa06-eba634dd1835",
  "context": {
    "created_at": "2025-10-23T14:05:38.140519",
    "previous_actions": [
      "plan_workflow",
      "workflow_planned",
      "executed_update_CUST001"
    ],
    "metadata": {
      "task_count": 3,
      "updated_fields": ["credit_limit", "subscription_plan"],
      "task_result": {"status": "success", "message": "Customer updated"}
    }
  }
}

2. Get updated fields for a workflow

Endpoint:

GET /api/workflows/{workflow_id}/updated-fields


Description:
Returns only the list of fields that were updated during the workflow execution.

Example Response:

{
  "workflow_id": "4d763c90-96ce-4365-aa06-eba634dd1835",
  "updated_fields": ["credit_limit", "subscription_plan"]
}


These endpoints are useful for auditing, debugging, or showing workflow progress in UI dashboards.

Example Usage
Updating Context in ExecutorAgent:
self.context_store.update_context(
    workflow_id,
    action="executed_update_CUST001",
    metadata={
        "customer_id": customer_id,
        "updated_fields": updated_fields,
        "task_result": {"status": "success"}
    }
)

Reading Updated Fields via API:
workflow_context = orchestrator.context_store.get_context(workflow_id)
updated_fields = workflow_context.get("metadata", {}).get("updated_fields", [])

Summary

The ContextStore is a central component of the context-aware ACL system. It:

Maintains workflow execution history

Tracks database updates per task

Supports auditing, monitoring, and debugging

Enables real-time context-aware orchestration

Provides API access for workflow context and updated fields