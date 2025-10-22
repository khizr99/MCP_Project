"""
Executor Agent
Performs actual database operations and system updates
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.models.message import AgentMessage, MessageResponse
from app.models.workflow import AgentType
from app.models.customer import CustomerCreate, CustomerUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.database import CustomerDB
import uuid


class ExecutorAgent(BaseAgent):
    """
    Executor Agent - Performs database operations and system updates
    
    Responsibilities:
    - Execute CRUD operations on customer data
    - Manage database transactions
    - Handle errors and rollbacks
    - Report execution results
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(AgentType.EXECUTOR, agent_id)
        self.db_session: Optional[AsyncSession] = None
        self.log("Executor Agent initialized")
    
    def set_db_session(self, session: AsyncSession):
        """Set database session for operations"""
        self.db_session = session
    
    async def process_message(self, message: AgentMessage) -> MessageResponse:
        """Process incoming message and route to appropriate handler"""
        self.log(f"Processing message: {message.action}")
        
        try:
            if message.action == "execute_operation":
                result = await self.execute_operation(message.payload)
            else:
                raise ValueError(f"Unknown action: {message.action}")
            
            return MessageResponse(
                success=True,
                message_id=message.message_id,
                result=result
            )
        except Exception as e:
            self.log(f"Error processing message: {str(e)}")
            return MessageResponse(
                success=False,
                message_id=message.message_id,
                error=str(e)
            )
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a database operation task"""
        self.status = "busy"
        self.log(f"Executing task: {task.get('description')}")
        
        try:
            if not self.db_session:
                raise RuntimeError("Database session not set")
            
            operation = task.get("parameters", {}).get("operation")
            params = task.get("parameters", {})
            
            if operation == "create":
                result = await self._create_customer(params)
            elif operation == "update":
                result = await self._update_customer(params)
            elif operation == "delete":
                result = await self._delete_customer(params)
            elif operation == "query":
                result = await self._query_customer(params)
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            self.status = "idle"
            return {
                "status": "success",
                "result": result,
                "message": f"Successfully executed {operation} operation"
            }
        except Exception as e:
            self.status = "idle"
            self.log(f"Task execution failed: {str(e)}")
            raise e
    
    async def execute_operation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a database operation"""
        operation = payload.get("operation")
        params = payload.get("parameters", {})
        
        self.log(f"Executing operation: {operation}")
        
        if operation == "create":
            return await self._create_customer(params)
        elif operation == "update":
            return await self._update_customer(params)
        elif operation == "delete":
            return await self._delete_customer(params)
        elif operation == "query":
            return await self._query_customer(params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _create_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer record"""
        try:
            # Generate new customer ID
            mcp_id = f"CUST{uuid.uuid4().hex[:6].upper()}"
            
            # Create customer object
            customer = CustomerDB(
                mcp_id=mcp_id,
                customer_name=params.get("customer_name"),
                email=params.get("email"),
                phone=params.get("phone"),
                credit_limit=params.get("credit_limit", 0.0),
                kyc_date=params.get("kyc_date", ""),
                status=params.get("status", "active"),
                region=params.get("region"),
                industry=params.get("industry"),
                country=params.get("country"),
                zip_code=params.get("zip_code"),
                subscription_plan=params.get("subscription_plan", "Basic"),
                signup_date=params.get("signup_date", ""),
                last_login=params.get("last_login", ""),
                total_transactions=0,
                total_spent=0.0,
                preferred_category=params.get("preferred_category"),
                loyalty_points=0,
                data=params.get("data")
            )
            
            self.db_session.add(customer)
            await self.db_session.commit()
            await self.db_session.refresh(customer)
            
            self.log(f"Created customer: {mcp_id}")
            
            return {
                "operation": "create",
                "customer_id": mcp_id,
                "success": True
            }
        except Exception as e:
            await self.db_session.rollback()
            raise e
    
    async def _update_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing customer record"""
        try:
            customer_id = params.get("target_customer_id") or params.get("customer_id")
            if not customer_id:
                raise ValueError("Customer ID is required for update")
            
            # Valid database columns for CustomerDB
            valid_columns = {
                "customer_name", "email", "phone", "credit_limit", "kyc_date",
                "status", "region", "industry", "country", "zip_code",
                "subscription_plan", "signup_date", "last_login",
                "total_transactions", "total_spent", "preferred_category",
                "loyalty_points", "data"
            }
            
            # Build update dictionary (exclude None values, operation keys, and invalid columns)
            update_data = {
                k: v for k, v in params.items() 
                if v is not None 
                and k not in ["operation", "target_customer_id", "customer_id", "parameters"]
                and k in valid_columns
            }
            
            if not update_data:
                raise ValueError("No update data provided")
            
            # Execute update
            stmt = (
                update(CustomerDB)
                .where(CustomerDB.mcp_id == customer_id)
                .values(**update_data)
            )
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            
            if result.rowcount == 0:
                raise ValueError(f"Customer {customer_id} not found")
            
            self.log(f"Updated customer: {customer_id}")
            
            return {
                "operation": "update",
                "customer_id": customer_id,
                "updated_fields": list(update_data.keys()),
                "success": True
            }
        except Exception as e:
            await self.db_session.rollback()
            raise e
    
    async def _delete_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a customer record"""
        try:
            customer_id = params.get("target_customer_id") or params.get("customer_id")
            if not customer_id:
                raise ValueError("Customer ID is required for delete")
            
            # Execute delete
            stmt = delete(CustomerDB).where(CustomerDB.mcp_id == customer_id)
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            
            if result.rowcount == 0:
                raise ValueError(f"Customer {customer_id} not found")
            
            self.log(f"Deleted customer: {customer_id}")
            
            return {
                "operation": "delete",
                "customer_id": customer_id,
                "success": True
            }
        except Exception as e:
            await self.db_session.rollback()
            raise e
    
    async def _query_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query customer data"""
        try:
            customer_id = params.get("target_customer_id") or params.get("customer_id")
            
            if customer_id:
                # Query specific customer
                stmt = select(CustomerDB).where(CustomerDB.mcp_id == customer_id)
                result = await self.db_session.execute(stmt)
                customer = result.scalar_one_or_none()
                
                if not customer:
                    raise ValueError(f"Customer {customer_id} not found")
                
                return {
                    "operation": "query",
                    "customer": {
                        "mcp_id": customer.mcp_id,
                        "customer_name": customer.customer_name,
                        "email": customer.email,
                        "status": customer.status,
                        "subscription_plan": customer.subscription_plan,
                        "credit_limit": customer.credit_limit,
                        "total_spent": customer.total_spent,
                        "loyalty_points": customer.loyalty_points
                    },
                    "success": True
                }
            else:
                # Query all customers (with limit)
                stmt = select(CustomerDB).limit(10)
                result = await self.db_session.execute(stmt)
                customers = result.scalars().all()
                
                return {
                    "operation": "query",
                    "customers": [
                        {
                            "mcp_id": c.mcp_id,
                            "customer_name": c.customer_name,
                            "email": c.email,
                            "status": c.status
                        } for c in customers
                    ],
                    "count": len(customers),
                    "success": True
                }
        except Exception as e:
            raise e
