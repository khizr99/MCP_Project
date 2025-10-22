# 👥 Team Member Setup Guide

## Welcome to the MCP Multi-Agent Orchestration Framework!

This guide will help you get the project running on your local machine.

---

## 📋 Prerequisites

Before you start, ensure you have:

- ✅ **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
  ```bash
  python --version
  ```
- ✅ **Git** installed ([Download](https://git-scm.com/downloads))
  ```bash
  git --version
  ```
- ✅ **GitHub Account** with repository access
- ✅ **Text Editor** (VS Code, PyCharm, or similar)

---

## 🚀 Quick Start (5 Minutes)

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/mcp-multi-agent-orchestration.git
cd mcp-multi-agent-orchestration
```

> Replace `YOUR_USERNAME` with the actual GitHub username/organization

---

### **Step 2: Create Virtual Environment**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### **Step 3: Install Dependencies**

**Standard Installation:**
```bash
pip install -r requirements.txt
```

**If Behind Corporate Firewall (SSL Issues):**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt
```

This will install:
- FastAPI - Web framework
- SQLAlchemy - Database ORM
- Pandas - Data processing
- Uvicorn - ASGI server
- And more...

---

### **Step 4: Configure Environment**

**Create your local `.env` file:**

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

**Edit `.env` (optional - defaults work fine):**
```bash
notepad .env    # Windows
nano .env       # Linux/Mac
```

Default configuration:
```env
APP_NAME=MCP Multi-Agent Orchestration
DEBUG=True
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite+aiosqlite:///./mcp_database.db
MAX_CONCURRENT_WORKFLOWS=5
```

---

### **Step 5: Run the Application**

```bash
python main.py
```

**Expected Output:**
```
🚀 Starting MCP Multi-Agent Orchestration System...
✓ Database initialized successfully
✓ Loaded 477 customers from CSV
✓ System ready!
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

### **Step 6: Open the API Documentation**

**In your browser, visit:**
- 📖 **API Docs (Swagger UI):** http://localhost:8000/docs
- 📊 **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- 🏠 **Health Check:** http://localhost:8000/health

---

## 🧪 Test the System

### **Option 1: Use Swagger UI**

1. Open http://localhost:8000/docs
2. Click on **GET /api/customers**
3. Click **"Try it out"**
4. Click **"Execute"**
5. You should see 477 customer records!

### **Option 2: Run Test Script**

```bash
python test_api.py
```

**Expected Output:**
```
✓ Health check passed
✓ Retrieved 10 customers
✓ Found specific customer
✓ Workflow created successfully
```

---

## 📁 Project Structure

```
mcp-multi-agent-orchestration/
├── app/
│   ├── agents/              # Agent implementations
│   │   ├── base_agent.py    # Abstract base agent
│   │   ├── planner_agent.py # Task planning agent
│   │   └── executor_agent.py # Execution agent
│   ├── models/              # Data models
│   │   ├── customer.py      # Customer schemas
│   │   ├── workflow.py      # Workflow schemas
│   │   └── message.py       # ACL protocol
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database layer
│   └── orchestrator.py      # Core orchestration engine
├── main.py                  # FastAPI application entry
├── requirements.txt         # Python dependencies
├── mcp_dataset.csv          # Sample customer data
└── test_api.py              # API tests
```

---

## 🛠️ Development Workflow

### **1. Create a Feature Branch**

```bash
git checkout -b feature/your-feature-name
```

Examples:
- `feature/add-validator-agent`
- `feature/notification-system`
- `fix/workflow-timeout`

### **2. Make Your Changes**

Edit code, add features, fix bugs...

### **3. Test Your Changes**

```bash
# Run the application
python main.py

# In another terminal, run tests
python test_api.py
```

### **4. Commit Your Changes**

```bash
git add .
git commit -m "feat: Add new feature description"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `refactor:` Code refactoring
- `test:` Adding tests

### **5. Push to GitHub**

```bash
git push origin feature/your-feature-name
```

### **6. Create Pull Request**

1. Go to GitHub repository
2. Click "Pull Requests" → "New Pull Request"
3. Select your branch
4. Add description of changes
5. Request review from team

---

## 🔄 Keep Your Code Updated

### **Pull Latest Changes from Main**

```bash
git checkout main
git pull origin main
```

### **Update Your Feature Branch**

```bash
git checkout feature/your-feature-name
git merge main
```

Or using rebase (keeps history cleaner):
```bash
git checkout feature/your-feature-name
git rebase main
```

---

## 📚 Key Endpoints to Know

### **Customer Management**
- `GET /api/customers` - List all customers
- `GET /api/customers/{id}` - Get specific customer
- `POST /api/customers/{id}/upgrade` - Quick upgrade

### **Workflow Management**
- `POST /api/workflows` - Create new workflow
- `GET /api/workflows/{id}` - Check workflow status
- `GET /api/workflows` - List all workflows

### **Agent Monitoring**
- `GET /api/agents/status` - Check agent health

### **System**
- `GET /health` - System health check
- `GET /` - API information

---

## 🐛 Common Issues & Solutions

### **Issue 1: "ModuleNotFoundError"**

**Symptom:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Reinstall dependencies
pip install -r requirements.txt
```

---

### **Issue 2: "Port 8000 already in use"**

**Symptom:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**

**Windows:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

**Or change the port in `.env`:**
```env
PORT=8001
```

---

### **Issue 3: SSL Certificate Errors**

**Symptom:**
```
SSLError: certificate verify failed
```

**Solution:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt
```

---

### **Issue 4: Database Locked**

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Stop the server (Ctrl+C)
# Delete the database file
del mcp_database.db  # Windows
rm mcp_database.db   # Linux/Mac

# Restart the application
python main.py
```

---

### **Issue 5: "Python not found"**

**Windows:**
- Add Python to PATH during installation
- Or use `py` instead of `python`

**Linux/Mac:**
- Use `python3` instead of `python`

---

## 🧪 Testing Guide

### **Manual Testing via Swagger UI**

1. **Create a Workflow:**
   ```
   POST /api/workflows
   {
     "name": "Test Workflow",
     "description": "Testing the system",
     "operation": "query",
     "target_customer_id": "CUST001",
     "parameters": {}
   }
   ```

2. **Check Status:**
   ```
   GET /api/workflows/{workflow_id}
   ```

3. **Verify Customer:**
   ```
   GET /api/customers/CUST001
   ```

### **Automated Testing**

```bash
# Run all tests
python test_api.py

# Or use pytest (Week 2)
pytest tests/
```

---

## 📖 Understanding the System

### **How It Works (High-Level)**

```
User Request → FastAPI Endpoint
    ↓
Orchestrator Creates Workflow
    ↓
Planner Generates Task Plan (3 tasks)
    ↓
Executor Executes Each Task:
  1. Validate Request
  2. Perform Operation (DB query/update)
  3. Validate Result
    ↓
Return Success Response
```

### **Agent Communication Protocol (ACL)**

Agents communicate using standardized JSON messages:

```json
{
  "message_id": "abc-123",
  "message_type": "TASK_REQUEST",
  "sender_id": "orchestrator",
  "receiver_id": "executor",
  "workflow_id": "workflow-456",
  "action": "update_customer",
  "payload": { ... },
  "priority": "MEDIUM"
}
```

See [`ACL_PROTOCOL.md`](ACL_PROTOCOL.md) for details.

---

## 🎯 Your First Contribution

### **Easy Starter Tasks:**

1. **Add a new documentation section**
   - Edit `README.md` or create new guide
   - Practice Git workflow

2. **Add logging to a function**
   - Pick any function in `app/agents/`
   - Add informative log messages

3. **Create a new test case**
   - Add test to `test_api.py`
   - Test edge cases

4. **Improve error messages**
   - Find a generic error message
   - Make it more descriptive

### **Ask for Help:**

- 💬 **Slack/Teams:** #mcp-dev-help channel
- 📧 **Email:** tech-lead@company.com
- 🐛 **GitHub Issues:** Report bugs or ask questions

---

## 📝 Code Style Guide

### **Python Conventions**

```python
# Use descriptive variable names
customer_name = "John Doe"  # ✅ Good
cn = "John Doe"             # ❌ Bad

# Add docstrings
def process_workflow(workflow_id: str) -> dict:
    """
    Process a workflow by executing its tasks.
    
    Args:
        workflow_id: Unique workflow identifier
        
    Returns:
        dict: Workflow execution results
    """
    pass

# Use type hints
def get_customer(customer_id: str) -> Customer:
    pass
```

### **Commit Messages**

```bash
# Good ✅
git commit -m "feat: Add customer validation to executor agent"
git commit -m "fix: Resolve database session timeout in workflows"
git commit -m "docs: Update API examples in README"

# Bad ❌
git commit -m "fixed stuff"
git commit -m "update"
git commit -m "asdfasdf"
```

---

## 🔒 Security Reminders

### **NEVER Commit:**
- ❌ `.env` file (use `.env.example`)
- ❌ Database files (`*.db`)
- ❌ API keys or passwords
- ❌ Personal credentials

### **ALWAYS:**
- ✅ Use `.env` for local configuration
- ✅ Keep dependencies updated
- ✅ Review code before committing
- ✅ Report security issues privately

---

## 📚 Additional Resources

### **Documentation**
- [`README.md`](README.md) - Project overview
- [`QUICK_START.md`](QUICK_START.md) - Quick start guide
- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) - Architecture details
- [`ACL_PROTOCOL.md`](ACL_PROTOCOL.md) - Communication protocol
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) - Common issues

### **External Resources**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)

---

## ✅ Setup Verification Checklist

Before you start coding, verify:

- [ ] Virtual environment activated (`(venv)` in prompt)
- [ ] All dependencies installed (`pip list` shows packages)
- [ ] Server runs without errors (`python main.py`)
- [ ] Can access http://localhost:8000/docs
- [ ] Test script passes (`python test_api.py`)
- [ ] `.env` file created and configured
- [ ] Git configured with your name/email

---

## 🎉 You're Ready!

Welcome to the team! If you have any questions, don't hesitate to ask.

**Happy Coding! 🚀**

---

**Last Updated:** 2025-10-22  
**Maintainer:** MCP Development Team
