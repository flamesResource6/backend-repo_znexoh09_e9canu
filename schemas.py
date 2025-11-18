"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

# Business-specific schemas for Chirag Battery

class Product(BaseModel):
    """
    Battery and inverter products
    Collection: "product"
    """
    name: str = Field(..., description="Product name")
    brand: Literal["Amaron", "Exide", "Luminous"] = Field(..., description="Brand name")
    type: Literal["bike-battery", "car-battery", "inverter", "inverter-battery"] = Field(..., description="Product type")
    capacity_ah: Optional[float] = Field(None, ge=0, description="Capacity in Ah where applicable")
    warranty_months: Optional[int] = Field(None, ge=0, description="Warranty in months")
    price: Optional[float] = Field(None, ge=0, description="Approximate MRP or selling price")
    description: Optional[str] = Field(None, description="Short description")
    in_stock: bool = Field(True, description="Availability status")

class Inquiry(BaseModel):
    """
    Customer inquiries and callbacks
    Collection: "inquiry"
    """
    name: str = Field(..., description="Customer name")
    phone: str = Field(..., description="Phone/WhatsApp number")
    message: Optional[str] = Field(None, description="Additional message or requirement")
    product_type: Optional[str] = Field(None, description="Requested product type e.g., car-battery")
    brand: Optional[str] = Field(None, description="Preferred brand")
    preferred_contact: Literal["call", "whatsapp"] = Field("whatsapp", description="Preferred contact method")
    city: Optional[str] = Field("Veraval, Gir Somnath", description="Customer city")
