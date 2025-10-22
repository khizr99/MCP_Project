# Agent Communication Protocol (ACL) Specification

## Overview

The Agent Communication Protocol (ACL) is a **standardized JSON-based message format** for inter-agent communication in the MCP Multi-Agent Orchestration Framework. This is one of the core reusable assets of the system.

## Purpose

- Enable **standardized communication** between all agents
- Provide **message tracking** and audit trails
- Support **asynchronous** and **synchronous** communication patterns
- Allow **flexible payload structures** for different operations
- Enable **error handling** and **acknowledgements**

## Message Structure

### Core Fields

```json
{
  "message_id": "string",           // Unique message identifier (UUID)
  "message_type": "string",         // Type: request, response, notification, error, ack
  "timestamp": "datetime",          // ISO 8601 format
  "priority": "string",             // low, medium, high, critical
  
  "sender_id": "string",            // Sending agent ID
  "sender_type": "string",          // Sending agent type (planner, executor, etc.)
  
  "receiver_id": "string",          // Target agent ID (null for broadcast)
  "receiver_type": "string",        // Target agent type
  
  "workflow_id": "string",          // Associated workflow ID
  "task_id": "string",              // Associated task ID (optional)
  
  "action": "string",               // Action to perform
  "payload": {},                    // Message data/parameters
  
  "in_reply_to": "string",          // Message ID being replied to (optional)
  "status": "string",               // Message processing status
  "error": "string",                // Error message (optional)
  
  "metadata": {}                    // Additional metadata (optional)
}
```

## Message Types

### 1. REQUEST
Used to request an action from another agent.

```json
{
  "message_type": "request",
  "sender_id": "orchestrator_1",
  "sender_type": "orchestrator",
  "receiver_id": "planner_1",
  "receiver_type": "planner",
  "workflow_id": "wf_12345",
  "action": "plan_workflow",
  "payload": {
    "operation": "update",
    "customer_id": "CUST001",
    "parameters": {
      "subscription_plan": "Premium"
    }
  }
}
```

### 2. RESPONSE
Reply to a previous request.

```json
{
  "message_type": "response",
  "sender_id": "planner_1",
  "sender_type": "planner",
  "receiver_id": "orchestrator_1",
  "receiver_type": "orchestrator",
  "workflow_id": "wf_12345",
  "action": "plan_complete",
  "in_reply_to": "msg_original_request",
  "payload": {
    "tasks": [
      {
        "task_id": "task_1",
        "description": "Validate update request",
        "agent_type": "planner"
      },
      {
        "task_id": "task_2",
        "description": "Execute database update",
        "agent_type": "executor"
      }
    ]
  },
  "status": "success"
}
```

### 3. NOTIFICATION
Inform other agents about an event (no response expected).

```json
{
  "message_type": "notification",
  "sender_id": "executor_1",
  "sender_type": "executor",
  "receiver_id": null,
  "workflow_id": "wf_12345",
  "action": "task_completed",
  "payload": {
    "task_id": "task_2",
    "result": "Database updated successfully",
    "affected_records": 1
  }
}
```

### 4. ERROR
Report an error condition.

```json
{
  "message_type": "error",
  "sender_id": "executor_1",
  "sender_type": "executor",
  "receiver_id": "orchestrator_1",
  "workflow_id": "wf_12345",
  "action": "execution_failed",
  "error": "Customer CUST999 not found",
  "payload": {
    "error_code": "NOT_FOUND",
    "customer_id": "CUST999"
  }
}
```

### 5. ACKNOWLEDGEMENT
Confirm receipt of a message.

```json
{
  "message_type": "ack",
  "sender_id": "executor_1",
  "receiver_id": "orchestrator_1",
  "in_reply_to": "msg_12345",
  "status": "received"
}
```

## Common Actions

### Planner Agent Actions
- `plan_workflow` - Generate task plan for a workflow
- `validate_request` - Validate if a request is feasible
- `plan_complete` - Return completed plan
- `validation_result` - Return validation results

### Executor Agent Actions
- `execute_operation` - Perform a database operation
- `execution_complete` - Report successful execution
- `execution_failed` - Report failed execution

### Orchestrator Actions
- `start_workflow` - Initiate a new workflow
- `task_assign` - Assign task to an agent
- `workflow_complete` - Workflow finished
- `workflow_failed` - Workflow failed

## Message Priority Levels

| Priority | Use Case | Response Time |
|----------|----------|---------------|
| **low** | Background tasks, logging | Best effort |
| **medium** | Standard operations | < 5 seconds |
| **high** | Important operations | < 2 seconds |
| **critical** | System errors, urgent updates | Immediate |

## Example: Complete Communication Flow

### Step 1: Orchestrator requests planning
```json
{
  "message_id": "msg_001",
  "message_type": "request",
  "sender_id": "orch_1",
  "sender_type": "orchestrator",
  "receiver_id": "planner_1",
  "receiver_type": "planner",
  "workflow_id": "wf_abc",
  "action": "plan_workflow",
  "payload": {
    "operation": "update",
    "target_customer_id": "CUST001",
    "parameters": {"credit_limit": 100000}
  },
  "priority": "high"
}
```

### Step 2: Planner responds with plan
```json
{
  "message_id": "msg_002",
  "message_type": "response",
  "sender_id": "planner_1",
  "receiver_id": "orch_1",
  "workflow_id": "wf_abc",
  "action": "plan_complete",
  "in_reply_to": "msg_001",
  "payload": {
    "tasks": [
      {"task_id": "t1", "description": "Fetch customer", "agent_type": "executor"},
      {"task_id": "t2", "description": "Update record", "agent_type": "executor"},
      {"task_id": "t3", "description": "Validate", "agent_type": "validator"}
    ]
  },
  "status": "success"
}
```

### Step 3: Orchestrator assigns task to executor
```json
{
  "message_id": "msg_003",
  "message_type": "request",
  "sender_id": "orch_1",
  "receiver_id": "executor_1",
  "receiver_type": "executor",
  "workflow_id": "wf_abc",
  "task_id": "t2",
  "action": "execute_operation",
  "payload": {
    "operation": "update",
    "customer_id": "CUST001",
    "credit_limit": 100000
  }
}
```

### Step 4: Executor responds with result
```json
{
  "message_id": "msg_004",
  "message_type": "response",
  "sender_id": "executor_1",
  "receiver_id": "orch_1",
  "workflow_id": "wf_abc",
  "task_id": "t2",
  "action": "execution_complete",
  "in_reply_to": "msg_003",
  "payload": {
    "operation": "update",
    "customer_id": "CUST001",
    "updated_fields": ["credit_limit"],
    "success": true
  },
  "status": "success"
}
```

## Implementation

The ACL is implemented in `app/models/message.py` using Pydantic models:

```python
from app.models.message import AgentMessage, MessageType, MessageResponse

# Create a message
message = AgentMessage(
    message_type=MessageType.REQUEST,
    sender_id="orch_1",
    sender_type="orchestrator",
    receiver_id="planner_1",
    receiver_type="planner",
    workflow_id="wf_123",
    action="plan_workflow",
    payload={"operation": "update"}
)

# Process message
response = await agent.process_message(message)
```

## Benefits

1. **Standardization**: All agents use the same message format
2. **Traceability**: Every message has a unique ID and timestamp
3. **Flexibility**: Payload can contain any operation-specific data
4. **Error Handling**: Built-in error reporting mechanism
5. **Asynchronous**: Supports both sync and async patterns
6. **Extensibility**: Easy to add new message types and actions
7. **Debugging**: Message history enables troubleshooting

## Best Practices

1. **Always set message_type correctly** for proper routing
2. **Use meaningful action names** that describe the intent
3. **Include workflow_id** for tracking and correlation
4. **Set appropriate priority** based on business importance
5. **Use in_reply_to** to maintain conversation threads
6. **Include error details** when status is failed
7. **Keep payloads focused** on specific operations
8. **Add metadata** for debugging information

## Future Extensions

Potential enhancements for Week 2+:
- Message encryption for sensitive data
- Message queuing with retry logic
- Broadcast messages to agent groups
- Message compression for large payloads
- Message TTL (time-to-live)
- Message acknowledgement tracking
- Performance metrics per message type

---

**This ACL specification is a core reusable asset that can be extended to support additional agent types and operations as the system grows.**
