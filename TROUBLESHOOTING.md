# Troubleshooting Guide

Common issues and their solutions for the MCP Multi-Agent Orchestration Framework.

---

## 🔴 Server Won't Start

### Problem: Import Error - "No module named 'fastapi'"
**Symptom**: Error when running `python main.py`
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:
```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Problem: Port 8000 Already in Use
**Symptom**: 
```
ERROR: [Errno 10048] error while attempting to bind on address
```

**Solution 1** - Stop other process:
```bash
# Windows - Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID)
taskkill /PID <PID> /F
```

**Solution 2** - Use different port:
Edit `.env` file:
```
PORT=8001
```

---

### Problem: Python Version Too Old
**Symptom**:
```
SyntaxError or "requires Python 3.9 or newer"
```

**Solution**:
```bash
# Check Python version
python --version

# If < 3.9, install Python 3.9+ from python.org
# Then recreate virtual environment
python -m venv venv
```

---

## 🔴 Database Issues

### Problem: Database Not Created
**Symptom**: No `mcp_database.db` file appears

**Solution**:
```bash
# Check CSV file exists
dir mcp_dataset.csv

# Delete old database if exists
del mcp_database.db

# Restart server (will recreate)
python main.py
```

---

### Problem: CSV Data Not Loading
**Symptom**: Console shows "Loaded 0 customers"

**Solution**:
```bash
# Verify CSV file size (should be ~1MB)
dir mcp_dataset.csv

# Ensure CSV is in project root
# Check CSV format (should have header row)

# If needed, delete database and restart
del mcp_database.db
python main.py
```

---

### Problem: Database Locked
**Symptom**:
```
sqlite3.OperationalError: database is locked
```

**Solution**:
```bash
# Stop all running servers
# Close any database browser tools
# Delete database file
del mcp_database.db
# Restart server
python main.py
```

---

## 🔴 API Issues

### Problem: 404 Not Found
**Symptom**: All API calls return 404

**Solution**:
```bash
# Verify server is running
# Check URL includes http://
curl http://localhost:8000/health

# Verify port number matches .env
# Default is 8000
```

---

### Problem: CORS Error in Browser
**Symptom**: Browser console shows CORS error

**Solution**:
This is normal for direct browser access. The API includes CORS middleware.

To test from browser, use:
- Swagger UI: http://localhost:8000/docs
- Or install browser CORS extension (for development only)

---

### Problem: Workflow Stays in "pending"
**Symptom**: Workflow never progresses

**Solution**:
```bash
# Check server console for errors
# Look for agent execution logs

# Verify workflow was created:
curl http://localhost:8000/api/workflows

# Check agent status:
curl http://localhost:8000/api/agents/status
```

---

## 🔴 Workflow Execution Issues

### Problem: "Customer not found" Error
**Symptom**: Workflow fails with customer not found

**Solution**:
```bash
# Verify customer exists:
curl http://localhost:8000/api/customers/CUST001

# List available customers:
curl http://localhost:8000/api/customers?limit=10

# Use valid customer ID from list
```

---

### Problem: Workflow Status 500 Error
**Symptom**: Internal server error when checking workflow

**Solution**:
```bash
# Check server console for detailed error
# Common causes:
# 1. Invalid workflow_id
# 2. Server restarted (workflows are in-memory)

# Restart server and create new workflow
```

---

### Problem: Database Update Not Working
**Symptom**: Workflow completes but data unchanged

**Solution**:
Check server console for execution logs. Verify:
```bash
# 1. Correct customer ID
# 2. Valid field names (check customer.py model)
# 3. Valid values for enums (status, subscription_plan)

# Example valid update:
{
  "target_customer_id": "CUST001",
  "parameters": {
    "subscription_plan": "Premium",  # Must be: Basic, Standard, or Premium
    "credit_limit": 100000
  }
}
```

---

## 🔴 Testing Issues

### Problem: test_api.py Connection Error
**Symptom**:
```
ConnectionError: Cannot connect to the API server
```

**Solution**:
```bash
# Ensure server is running in another terminal
python main.py

# In new terminal, run tests
python test_api.py

# Verify port matches (default 8000)
```

---

### Problem: Tests Fail Intermittently
**Symptom**: Some tests pass, some fail randomly

**Solution**:
```bash
# Add delay between tests
# Workflows may still be processing

# Run tests one at a time:
curl http://localhost:8000/health
# wait 1 second
curl http://localhost:8000/api/customers
```

---

## 🔴 Setup Script Issues

### Problem: setup.bat Fails
**Symptom**: Setup script exits with error

**Solution**:
```bash
# Run steps manually:

# 1. Create venv
python -m venv venv

# 2. Activate
venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copy .env
copy .env.example .env
```

---

### Problem: Virtual Environment Won't Activate
**Symptom**: `venv\Scripts\activate` does nothing

**Solution Windows PowerShell**:
```powershell
# May need to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
venv\Scripts\Activate.ps1
```

**Solution Command Prompt**:
```cmd
# Use .bat instead
venv\Scripts\activate.bat
```

---

## 🔴 Performance Issues

### Problem: Slow API Response
**Symptom**: Requests take > 5 seconds

**Solution**:
```bash
# Check database size
dir mcp_database.db

# If very large, reset:
del mcp_database.db
python main.py

# Enable debug logging in .env:
DEBUG=True

# Check server console for bottlenecks
```

---

### Problem: High Memory Usage
**Symptom**: Server uses > 500MB RAM

**Solution**:
```bash
# Normal usage is 50-100MB
# Check for:
# 1. Too many concurrent workflows
# 2. Large payloads in messages
# 3. Memory leaks (restart server periodically)

# Restart server:
Ctrl+C
python main.py
```

---

## 🔴 Code Issues

### Problem: Import Errors in Code
**Symptom**: Can't import app modules

**Solution**:
```bash
# Ensure all __init__.py files exist:
app\__init__.py
app\models\__init__.py
app\agents\__init__.py

# Run from project root, not subdirectory
cd c:\Users\MohammadKhizrHaidar\Downloads\MCP
python main.py
```

---

### Problem: Type Checking Errors
**Symptom**: IDE shows red underlines

**Solution**:
These are mostly type hints warnings and won't affect runtime.

For development:
```bash
# Install type stubs
pip install types-all

# Or ignore type checking
# Code will still work
```

---

## 🔴 Agent Issues

### Problem: Planner Agent Not Responding
**Symptom**: Workflows stuck at planning stage

**Check Server Console**:
Look for:
```
[planner:planner_xxxxx] Processing message: plan_workflow
```

If missing:
```bash
# Restart server
# Check app/agents/planner_agent.py exists
# Verify no syntax errors in agent code
```

---

### Problem: Executor Agent Errors
**Symptom**: Database operations fail

**Check**:
1. Database session is set
2. Valid SQL operations
3. Customer ID exists

**Server console should show**:
```
[executor:executor_xxxxx] Executing task: ...
[executor:executor_xxxxx] Updated customer: CUST001
```

---

## 🔴 Documentation Issues

### Problem: Swagger UI Not Loading
**Symptom**: http://localhost:8000/docs shows error

**Solution**:
```bash
# Ensure server is running
# Clear browser cache
# Try different browser
# Check server console for errors

# Verify FastAPI is installed:
pip show fastapi
```

---

## 🟡 Common Warnings (Safe to Ignore)

These warnings are normal and won't affect functionality:

```
WARNING: Type hint errors (basedpyright)
WARNING: SQLAlchemy deprecation warnings
WARNING: Pydantic v2 migration warnings
```

---

## 🛠️ Debug Mode

Enable detailed logging:

**Edit .env**:
```
DEBUG=True
```

**Restart server** - will show:
- All SQL queries
- Detailed error traces
- Agent message contents
- Workflow state changes

---

## 📞 Still Having Issues?

### Checklist Before Asking for Help

1. [ ] Checked this troubleshooting guide
2. [ ] Read error message carefully
3. [ ] Checked server console output
4. [ ] Verified setup with SETUP_VERIFICATION.md
5. [ ] Tried restarting server
6. [ ] Deleted and recreated database
7. [ ] Reinstalled dependencies

### Information to Provide

When reporting issues, include:
- **Error message** (full text)
- **Server console output** (last 20 lines)
- **Python version**: `python --version`
- **OS**: Windows/Linux/Mac
- **What you were trying to do**
- **Steps to reproduce**

---

## 🔄 Nuclear Option (Complete Reset)

If all else fails:

```bash
# 1. Stop server (Ctrl+C)

# 2. Delete everything except source code
del mcp_database.db
rmdir /s venv

# 3. Start fresh
setup.bat

# 4. Run server
run.bat

# 5. Test
python test_api.py
```

---

## ✅ Quick Diagnostic Commands

```bash
# Check Python
python --version

# Check pip
pip --version

# Check venv active
where python
# Should show: ...\venv\Scripts\python.exe

# Check dependencies
pip list | findstr fastapi

# Check server running
netstat -an | findstr :8000

# Check database
dir mcp_database.db

# Check API
curl http://localhost:8000/health
```

---

**Most issues are resolved by:**
1. Activating virtual environment
2. Installing dependencies
3. Restarting server
4. Using correct URLs/IDs

**Good luck! 🚀**
