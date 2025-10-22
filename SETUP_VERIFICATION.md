# Setup Verification Checklist

## 📋 Pre-Flight Checklist

Use this checklist to verify your Week 1 MVP setup is complete and working.

---

## ✅ File Structure Verification

Check that all files exist:

```
[ ] mcp_dataset.csv (should be ~1MB)
[ ] main.py
[ ] requirements.txt
[ ] .env
[ ] setup.bat
[ ] run.bat
[ ] test_api.py

[ ] app/
    [ ] __init__.py
    [ ] config.py
    [ ] database.py
    [ ] orchestrator.py
    
    [ ] models/
        [ ] __init__.py
        [ ] customer.py
        [ ] workflow.py
        [ ] message.py
    
    [ ] agents/
        [ ] __init__.py
        [ ] base_agent.py
        [ ] planner_agent.py
        [ ] executor_agent.py

[ ] README.md
[ ] QUICK_START.md
[ ] ACL_PROTOCOL.md
[ ] PROJECT_STRUCTURE.md
[ ] WEEK1_SUMMARY.md
```

**Status**: ______ files present / 23 total

---

## ✅ Environment Setup

### 1. Python Version
```bash
python --version
```
Expected: Python 3.9 or higher  
**Result**: ___________________

### 2. Virtual Environment Created
```bash
dir venv
# or
ls venv
```
**Exists**: [ ] Yes [ ] No

### 3. Dependencies Installed
```bash
pip list
```
Check for:
- [ ] fastapi
- [ ] uvicorn
- [ ] pydantic
- [ ] sqlalchemy
- [ ] pandas

**All present**: [ ] Yes [ ] No

---

## ✅ Server Startup Test

### 1. Start the Server
```bash
python main.py
```

### 2. Check Console Output
You should see:
```
🚀 Starting MCP Multi-Agent Orchestration System...
✓ Database initialized successfully
✓ Loaded 477 customers from CSV
✓ System ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Checklist**:
- [ ] No import errors
- [ ] Database initialized message appears
- [ ] CSV loaded (477 customers)
- [ ] Server running on port 8000
- [ ] No error messages

---

## ✅ API Endpoint Tests

Keep server running, open new terminal for these tests:

### 1. Health Check
```bash
curl http://localhost:8000/health
```
**Expected**: `{"status":"healthy", ...}`  
**Result**: [ ] Pass [ ] Fail

### 2. Root Endpoint
```bash
curl http://localhost:8000/
```
**Expected**: `{"message":"MCP Multi-Agent...", "status":"running"}`  
**Result**: [ ] Pass [ ] Fail

### 3. API Documentation
Open in browser: http://localhost:8000/docs  
**Expected**: Swagger UI with 12+ endpoints  
**Result**: [ ] Pass [ ] Fail

### 4. List Customers
```bash
curl http://localhost:8000/api/customers?limit=5
```
**Expected**: JSON array with 5 customers  
**Result**: [ ] Pass [ ] Fail

### 5. Get Specific Customer
```bash
curl http://localhost:8000/api/customers/CUST001
```
**Expected**: Single customer object  
**Result**: [ ] Pass [ ] Fail

### 6. Agent Status
```bash
curl http://localhost:8000/api/agents/status
```
**Expected**: Planner and Executor agent info  
**Result**: [ ] Pass [ ] Fail

---

## ✅ Workflow Functionality Test

### 1. Create Workflow
```bash
curl -X POST "http://localhost:8000/api/workflows" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Workflow\",\"operation\":\"update\",\"target_customer_id\":\"CUST001\",\"parameters\":{\"credit_limit\":50000}}"
```

**Checklist**:
- [ ] Response includes workflow_id
- [ ] Status is "pending" or "running"
- [ ] No error messages

Copy workflow_id: ____________________

### 2. Check Workflow Status
```bash
curl http://localhost:8000/api/workflows/{workflow_id}
```

**Checklist**:
- [ ] Status shows workflow progress
- [ ] Progress percentage visible
- [ ] Current task information present

### 3. List All Workflows
```bash
curl http://localhost:8000/api/workflows
```
**Expected**: Array with at least 1 workflow  
**Result**: [ ] Pass [ ] Fail

---

## ✅ Automated Test Script

### Run Complete Test Suite
```bash
python test_api.py
```

**Expected Output Sections**:
- [ ] Health Check
- [ ] List Customers
- [ ] Get Customer
- [ ] Agent Status
- [ ] Create Workflow
- [ ] Workflow Status
- [ ] List All Workflows
- [ ] Quick Upgrade

**All tests pass**: [ ] Yes [ ] No

---

## ✅ Database Verification

### 1. Database File Exists
```bash
dir mcp_database.db
# or
ls -l mcp_database.db
```
**Exists**: [ ] Yes [ ] No  
**Size**: _______ KB (should be > 100 KB)

### 2. Customer Count
Via API:
```bash
curl http://localhost:8000/api/customers?limit=500 | grep mcp_id | wc -l
```
**Expected**: 477 customers  
**Result**: _______ customers

---

## ✅ Agent Communication Test

### Watch Console Output
While running workflows, check server console for:

```
[TIMESTAMP] [ORCHESTRATOR] Created workflow: wf_xxxxx
[TIMESTAMP] [ORCHESTRATOR] Planning workflow: wf_xxxxx
[TIMESTAMP] [planner:planner_xxxxx] Processing message: plan_workflow
[TIMESTAMP] [ORCHESTRATOR] Generated X tasks for workflow
[TIMESTAMP] [ORCHESTRATOR] Starting workflow execution
[TIMESTAMP] [executor:executor_xxxxx] Processing message: execute_operation
[TIMESTAMP] [executor:executor_xxxxx] Updated customer: CUST001
```

**Checklist**:
- [ ] Orchestrator messages appear
- [ ] Planner agent messages appear
- [ ] Executor agent messages appear
- [ ] Workflow completion logged

---

## ✅ Error Handling Test

### Test Invalid Customer ID
```bash
curl http://localhost:8000/api/customers/INVALID999
```
**Expected**: 404 error with message  
**Result**: [ ] Pass [ ] Fail

### Test Invalid Workflow
```bash
curl http://localhost:8000/api/workflows/invalid-id
```
**Expected**: 404 error  
**Result**: [ ] Pass [ ] Fail

---

## ✅ Performance Check

### Server Response Times
All should be under 1 second:

- [ ] Health check: _______ ms
- [ ] List customers: _______ ms
- [ ] Get customer: _______ ms
- [ ] Create workflow: _______ ms

**All under 1 second**: [ ] Yes [ ] No

---

## ✅ Documentation Review

### Files Readable
- [ ] README.md opens and is formatted correctly
- [ ] QUICK_START.md is clear and understandable
- [ ] ACL_PROTOCOL.md has code examples
- [ ] PROJECT_STRUCTURE.md shows file tree

### API Documentation
- [ ] Swagger UI (http://localhost:8000/docs) loads
- [ ] All endpoints visible
- [ ] Can execute test requests from Swagger UI

---

## ✅ Code Quality Check

### No Syntax Errors
```bash
python -m py_compile main.py
python -m py_compile app/orchestrator.py
python -m py_compile app/agents/planner_agent.py
python -m py_compile app/agents/executor_agent.py
```
**All compile**: [ ] Yes [ ] No

### Import Check
```bash
python -c "from app.orchestrator import orchestrator; print('OK')"
python -c "from app.agents import PlannerAgent, ExecutorAgent; print('OK')"
python -c "from app.models.message import AgentMessage; print('OK')"
```
**All import**: [ ] Yes [ ] No

---

## 📊 Final Score

Count your checkmarks:

- **File Structure**: _____ / 23
- **Environment Setup**: _____ / 5
- **Server Startup**: _____ / 5
- **API Endpoints**: _____ / 6
- **Workflow Tests**: _____ / 5
- **Database**: _____ / 2
- **Agent Communication**: _____ / 4
- **Error Handling**: _____ / 2
- **Performance**: _____ / 4
- **Documentation**: _____ / 5
- **Code Quality**: _____ / 5

**TOTAL**: _____ / 66

### Rating
- **60-66**: Excellent! Everything working perfectly ✅
- **50-59**: Good! Minor issues to fix 👍
- **40-49**: Needs attention. Review failed items ⚠️
- **< 40**: Setup incomplete. Start over with QUICK_START.md ❌

---

## 🔧 Troubleshooting

### If Server Won't Start
1. Check Python version (3.9+)
2. Activate virtual environment
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Check if port 8000 is available
5. Review error messages in console

### If Database Issues
1. Delete `mcp_database.db`
2. Ensure `mcp_dataset.csv` exists
3. Restart server (will recreate database)

### If Import Errors
1. Ensure virtual environment is activated
2. Check that app/ folder has __init__.py files
3. Run from project root directory
4. Reinstall dependencies

### If Tests Fail
1. Ensure server is running
2. Check that you're using localhost:8000
3. Wait a few seconds between workflow tests
4. Check server console for errors

---

## ✅ Verification Complete!

Date: ______________  
Verified by: ______________  
Status: [ ] Ready for Week 2 [ ] Needs fixes

**Notes**:
_______________________________________________________
_______________________________________________________
_______________________________________________________

---

**If all checks pass, you're ready to proceed to Week 2! 🚀**
