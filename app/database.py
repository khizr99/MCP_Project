"""
Database Module
Handles all database operations for the MCP system
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, Text
from datetime import datetime
from app.config import settings
import pandas as pd
import json


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class CustomerDB(Base):
    """SQLAlchemy model for Customer table"""
    __tablename__ = "customers"
    
    mcp_id = Column(String, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String)
    credit_limit = Column(Float, default=0.0)
    kyc_date = Column(String)
    status = Column(String, default="active")
    region = Column(String)
    industry = Column(String, index=True)
    country = Column(String)
    zip_code = Column(String)
    subscription_plan = Column(String, default="Basic")
    signup_date = Column(String)
    last_login = Column(String)
    total_transactions = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    preferred_category = Column(String)
    loyalty_points = Column(Integer, default=0)
    data = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowDB(Base):
    """SQLAlchemy model for Workflow table"""
    __tablename__ = "workflows"
    
    workflow_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="pending")
    tasks = Column(JSON)
    current_task_index = Column(Integer, default=0)
    context = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database and create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database initialized successfully")


async def load_csv_data():
    """Load data from CSV into database"""
    try:
        # Read CSV file
        df = pd.read_csv("mcp_dataset.csv")
        
        async with AsyncSessionLocal() as session:
            # Check if data already exists
            from sqlalchemy import select
            result = await session.execute(select(CustomerDB).limit(1))
            if result.scalar_one_or_none():
                print("✓ Database already populated")
                return
            
            # Process and insert data
            for _, row in df.iterrows():
                # Parse the data column if it's a string
                data_value = row.get('data')
                if pd.notna(data_value) and isinstance(data_value, str):
                    try:
                        data_value = json.loads(data_value)
                    except:
                        data_value = {"raw": str(data_value)}
                
                customer = CustomerDB(
                    mcp_id=row['mcp_id'],
                    customer_name=row['customer_name'],
                    email=row['email'],
                    phone=str(row['phone']),
                    credit_limit=float(row['credit_limit']),
                    kyc_date=str(row['kyc_date']),
                    status=row['status'],
                    region=row['region'],
                    industry=row['industry'],
                    country=row['country'],
                    zip_code=str(row['zip_code']),
                    subscription_plan=row['subscription_plan'],
                    signup_date=str(row['signup_date']),
                    last_login=str(row['last_login']),
                    total_transactions=int(row['total_transactions']),
                    total_spent=float(row['total_spent']),
                    preferred_category=row['preferred_category'],
                    loyalty_points=int(row['loyalty_points']),
                    data=data_value
                )
                session.add(customer)
            
            await session.commit()
            print(f"✓ Loaded {len(df)} customers from CSV")
            
    except Exception as e:
        print(f"✗ Error loading CSV data: {e}")


async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
