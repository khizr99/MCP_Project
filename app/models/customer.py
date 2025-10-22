"""
Customer Profile Models
Represents the Master Customer Profile (MCP) data structure
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CustomerStatus(str, Enum):
    """Customer account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class SubscriptionPlan(str, Enum):
    """Available subscription plans"""
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"


class Customer(BaseModel):
    """Complete customer profile"""
    mcp_id: str = Field(..., description="Unique customer identifier")
    customer_name: str = Field(..., description="Customer company name")
    email: EmailStr = Field(..., description="Customer email address")
    phone: str = Field(..., description="Customer phone number")
    credit_limit: float = Field(..., ge=0, description="Credit limit")
    kyc_date: str = Field(..., description="KYC completion date")
    status: CustomerStatus = Field(..., description="Account status")
    region: str = Field(..., description="Customer region/city")
    industry: str = Field(..., description="Industry sector")
    country: str = Field(..., description="Country")
    zip_code: str = Field(..., description="Zip/postal code")
    subscription_plan: SubscriptionPlan = Field(..., description="Subscription tier")
    signup_date: str = Field(..., description="Account creation date")
    last_login: str = Field(..., description="Last login date")
    total_transactions: int = Field(..., ge=0, description="Total transaction count")
    total_spent: float = Field(..., ge=0, description="Total amount spent")
    preferred_category: str = Field(..., description="Preferred product category")
    loyalty_points: int = Field(..., ge=0, description="Loyalty points balance")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mcp_id": "CUST001",
                "customer_name": "Johnson Group",
                "email": "contact@johnsongroup.com",
                "phone": "5831580044",
                "credit_limit": 48983.0,
                "kyc_date": "7/3/2021",
                "status": "active",
                "region": "Lake Jesseberg",
                "industry": "IT",
                "country": "USA",
                "zip_code": "67390",
                "subscription_plan": "Standard",
                "signup_date": "6/20/2021",
                "last_login": "10/30/2023",
                "total_transactions": 65,
                "total_spent": 17349.38,
                "preferred_category": "Books",
                "loyalty_points": 758,
                "data": {"preferred_contact": "email"}
            }
        }


class CustomerCreate(BaseModel):
    """Data required to create a new customer"""
    customer_name: str
    email: EmailStr
    phone: str
    credit_limit: float = Field(default=0.0, ge=0)
    region: str
    industry: str
    country: str
    zip_code: str
    subscription_plan: SubscriptionPlan = SubscriptionPlan.BASIC
    preferred_category: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class CustomerUpdate(BaseModel):
    """Data that can be updated for a customer"""
    customer_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    credit_limit: Optional[float] = Field(default=None, ge=0)
    status: Optional[CustomerStatus] = None
    region: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    preferred_category: Optional[str] = None
    loyalty_points: Optional[int] = Field(default=None, ge=0)
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "active",
                "credit_limit": 50000.0,
                "subscription_plan": "Premium"
            }
        }
