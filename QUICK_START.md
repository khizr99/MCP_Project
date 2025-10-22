# Quick Start Guide - Week 1 MVP

## 🚀 Get Started in 5 Minutes

### Step 1: Setup (One-time)

**Option A: Automatic Setup (Windows)**
```bash
# Run the automated setup script
setup.bat
```

**Option B: Manual Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
```

### Step 2: Start the Server

```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Start the server
python main.py
```

You should see:
```
🚀 Starting MCP Multi-Agent Orchestration System...
✓ Database initialized successfully
✓ Loaded 477 customers from CSV
✓ System ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test the API

**Option 1: Use the Browser**
- Open http://localhost:8000/docs for interactive API documentation
- Try the `/health` endpoint

**Option 2: Run the test script**
```bash
# In a new terminal (keep server running)
python test_api.py
```

**Option 3: Use curl**
```bash
# Check health
curl http://localhost:8000/health

# List customers
curl http://localhost:8000/api/customers

# Get specific customer
curl http://localhost:8000/api/customers/CUST001
```

### Step 4: Create Your First Workflow

Using the browser (http://localhost:8000/docs):
1. Find the `POST /api/workflows` endpoint
2. Click "Try it out"
3. Use this example:

```json
{
  "name": "My First Workflow",
  "description": "Test updating a customer",
  "operation": "update",
  "target_customer_id": "CUST001",
  "parameters": {
    "credit_limit": 75000,
    "subscription_plan": "Premium"
  }
}
```

4. Click "Execute"
5. Copy the `workflow_id` from the response
6. Use `GET /api/workflows/{workflow_id}` to check status

## 🧪 Example Workflows

### 1. Update Customer Subscription
```json
{
  "name": "Upgrade to Premium",
  "operation": "update",
  "target_customer_id": "CUST001",
  "parameters": {
    "subscription_plan": "Premium"
  }
}
```

### 2. Update Credit Limit
```json
{
  "name": "Increase Credit Limit",
  "operation": "update",
  "target_customer_id": "CUST002",
  "parameters": {
    "credit_limit": 100000
  }
}
```

### 3. Query Customer
```json
{
  "name": "Fetch Customer Data",
  "operation": "query",
  "target_customer_id": "CUST001",
  "parameters": {}
}
```

### 4. Multiple Updates
```json
{
  "name": "Complete Profile Update",
  "operation": "update",
  "target_customer_id": "CUST003",
  "parameters": {
    "subscription_plan": "Premium",
    "credit_limit": 150000,
    "status": "active"
  }
}
```

## 📊 Understanding the System

### What happens when you create a workflow?

1. **Orchestrator** receives your request
2. **Planner Agent** generates a task list:
   - Validate request
   - Execute operation
   - Validate result
3. **Executor Agent** performs the database operation
4. **Orchestrator** tracks progress and updates workflow state

### Workflow States

- `pending` - Workflow created, waiting to start
- `running` - Currently executing tasks
- `completed` - All tasks finished successfully
- `failed` - Execution failed (check error field)

### Checking Workflow Progress

```bash
# Get workflow status
curl http://localhost:8000/api/workflows/{workflow_id}

# Response includes:
# - status: current state
# - progress: percentage (0-100)
# - current_task: what's happening now
```

## 🔍 Exploring the System

### View All Workflows
```bash
curl http://localhost:8000/api/workflows
```

### View Agent Status
```bash
curl http://localhost:8000/api/agents/status
```

### Browse Customers
```bash
# First 10 customers
curl http://localhost:8000/api/customers

# With pagination
curl "http://localhost:8000/api/customers?skip=10&limit=20"
```

## 🛠️ Troubleshooting

### Server won't start
- Make sure virtual environment is activated
- Check if port 8000 is available
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Database errors
- The database is auto-created on first run
- CSV file must be in the project root: `mcp_dataset.csv`
- Delete `mcp_database.db` and restart to reset

### Import errors
- Make sure you're in the project directory
- Virtual environment must be activated
- Try: `pip install --upgrade -r requirements.txt`

## 📚 Next Steps

Once comfortable with basics:

1. **Explore the Code**
   - `app/orchestrator.py` - See how workflows are managed
   - `app/agents/planner_agent.py` - Understand task planning
   - `app/agents/executor_agent.py` - See database operations
   - `app/models/message.py` - Learn the communication protocol

2. **Experiment**
   - Try different update operations
   - Create workflows for multiple customers
   - Monitor agent status during execution
   - Check workflow history

3. **Extend**
   - Add custom validation logic
   - Create new agent types
   - Add more complex operations
   - Implement additional workflows

## 🎯 Key Features to Try

### Quick Operations
Convenient shortcuts for common tasks:

```bash
# Upgrade customer subscription
curl -X POST "http://localhost:8000/api/customers/CUST001/upgrade?subscription_plan=Premium"

# Update credit limit
curl -X POST "http://localhost:8000/api/customers/CUST001/update-credit?credit_limit=80000"
```

### Interactive Documentation
The FastAPI Swagger UI (http://localhost:8000/docs) lets you:
- See all available endpoints
- Try API calls directly in browser
- View request/response schemas
- Download OpenAPI specification

### Real Dataset
The system includes 477 real customer records with:
- Various industries and regions
- Different subscription levels
- Transaction histories
- Loyalty points

## 💡 Tips

1. **Keep the server running** - It watches for file changes and auto-reloads
2. **Check logs** - The terminal shows all orchestrator and agent activity
3. **Use the docs** - http://localhost:8000/docs is the easiest way to test
4. **Start simple** - Try single-field updates before complex ones
5. **Monitor workflows** - Watch the status change from pending → running → completed

## ⚡ Common Commands

```bash
# Start server
python main.py

# Run tests
python test_api.py

# Check health
curl http://localhost:8000/health

# Create workflow (PowerShell)
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/workflows" `
  -ContentType "application/json" `
  -Body '{"name":"Test","operation":"update","target_customer_id":"CUST001","parameters":{"credit_limit":50000}}'
```

---

**You're all set! Start experimenting with the Multi-Agent Orchestration Framework! 🎉**
