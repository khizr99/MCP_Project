# MCP_Project/main.py

"""
FastAPI Application
Main API endpoints for the MCP Multi-Agent Orchestration system
With context-aware ACL integration
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, load_csv_data, get_db, CustomerDB
from app.models.customer import Customer
from app.models.workflow import WorkflowRequest, WorkflowResponse
from app.orchestrator import orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting MCP Multi-Agent Orchestration System...")
    await init_db()
    await load_csv_data()
    print("✓ System ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent Orchestration Framework for Master Customer Profile Management",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================ 
# HEALTH CHECK ENDPOINTS
# ============================================================================ 

@app.get("/")
async def root():
    return {
        "message": "MCP Multi-Agent Orchestration System",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2025-10-23T16:00:00Z"
    }

# ============================================================================ 
# CUSTOMER (MCP) ENDPOINTS
# ============================================================================ 

@app.get("/api/customers", response_model=List[Customer])
async def list_customers(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(CustomerDB).offset(skip).limit(limit)
    result = await db.execute(stmt)
    customers = result.scalars().all()
    return [
        Customer(
            mcp_id=c.mcp_id,
            customer_name=c.customer_name,
            email=c.email,
            phone=c.phone,
            credit_limit=c.credit_limit,
            kyc_date=c.kyc_date,
            status=c.status,
            region=c.region,
            industry=c.industry,
            country=c.country,
            zip_code=c.zip_code,
            subscription_plan=c.subscription_plan,
            signup_date=c.signup_date,
            last_login=c.last_login,
            total_transactions=c.total_transactions,
            total_spent=c.total_spent,
            preferred_category=c.preferred_category,
            loyalty_points=c.loyalty_points,
            data=c.data
        )
        for c in customers
    ]


@app.get("/api/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(CustomerDB).where(CustomerDB.mcp_id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return Customer(
        mcp_id=customer.mcp_id,
        customer_name=customer.customer_name,
        email=customer.email,
        phone=customer.phone,
        credit_limit=customer.credit_limit,
        kyc_date=customer.kyc_date,
        status=customer.status,
        region=customer.region,
        industry=customer.industry,
        country=customer.country,
        zip_code=customer.zip_code,
        subscription_plan=customer.subscription_plan,
        signup_date=customer.signup_date,
        last_login=customer.last_login,
        total_transactions=customer.total_transactions,
        total_spent=customer.total_spent,
        preferred_category=customer.preferred_category,
        loyalty_points=customer.loyalty_points,
        data=customer.data
    )

# ============================================================================ 
# WORKFLOW & ORCHESTRATION ENDPOINTS
# ============================================================================ 

@app.post("/api/workflows", response_model=WorkflowResponse)
async def create_workflow(request: WorkflowRequest, db: AsyncSession = Depends(get_db)):
    try:
        response = await orchestrator.create_workflow(request, db)
        # Debug: print context
        workflow_context = orchestrator.context_store.get_context(response.workflow_id)
        if workflow_context:
            print(f"🔹 Context for workflow {response.workflow_id}: {workflow_context}")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(workflow_id: str):
    response = await orchestrator.get_workflow_status(workflow_id)
    if not response:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return response


@app.get("/api/workflows")
async def list_workflows():
    return orchestrator.list_workflows()


# ============================================================================ 
# AGENT STATUS ENDPOINTS
# ============================================================================ 

@app.get("/api/agents/status")
async def get_agents_status():
    return {
        "planner": {
            "agent_id": orchestrator.planner_agent.agent_id,
            "type": "planner",
            "status": orchestrator.planner_agent.status
        },
        "executor": {
            "agent_id": orchestrator.executor_agent.agent_id,
            "type": "executor",
            "status": orchestrator.executor_agent.status
        }
    }

# ============================================================================ 
# QUICK OPERATION ENDPOINTS
# ============================================================================ 

@app.post("/api/customers/{customer_id}/upgrade")
async def upgrade_customer(customer_id: str, subscription_plan: str, db: AsyncSession = Depends(get_db)):
    request = WorkflowRequest(
        name=f"Upgrade {customer_id} Subscription",
        description=f"Upgrade customer to {subscription_plan}",
        operation="update",
        target_customer_id=customer_id,
        parameters={"subscription_plan": subscription_plan}
    )
    return await create_workflow(request, db)


@app.post("/api/customers/{customer_id}/update-credit")
async def update_credit_limit(customer_id: str, credit_limit: float, db: AsyncSession = Depends(get_db)):
    request = WorkflowRequest(
        name=f"Update {customer_id} Credit Limit",
        description=f"Update credit limit to {credit_limit}",
        operation="update",
        target_customer_id=customer_id,
        parameters={"credit_limit": credit_limit}
    )
    return await create_workflow(request, db)

# ============================================================================ 
# CONTEXT STORE ENDPOINTS
# ============================================================================ 

# ============================================================================ 
# CONTEXT STORE ENDPOINTS
# ============================================================================ 

@app.get("/api/context/{workflow_id}")
async def get_workflow_context(workflow_id: str):
    """Get the context for a specific workflow"""
    context = orchestrator.context_store.get_context(workflow_id)
    if context is None:
        return {"workflow_id": workflow_id, "context": []}
    return {"workflow_id": workflow_id, "context": context}



@app.delete("/api/context/{workflow_id}")
async def clear_context(workflow_id: str):
    """Clear context for a workflow"""
    success = orchestrator.context_store.clear_context(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"No context found to clear for workflow {workflow_id}")
    return {"workflow_id": workflow_id, "status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
