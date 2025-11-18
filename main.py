import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Product as ProductSchema, Inquiry as InquirySchema

app = FastAPI(title="Chirag Battery API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Helpers ----------
BRANDS = ["Amaron", "Exide", "Luminous"]
TYPES = ["bike-battery", "car-battery", "inverter", "inverter-battery"]


# ---------- Startup: seed sample products if empty ----------
@app.on_event("startup")
async def seed_products():
    if db is None:
        return
    try:
        count = db["product"].count_documents({})
        if count == 0:
            samples = [
                {"name": "Amaron Pro Rider", "brand": "Amaron", "type": "bike-battery", "capacity_ah": 9.0, "warranty_months": 48, "price": 1699.0, "description": "Maintenance-free bike battery", "in_stock": True},
                {"name": "Exide Xplore", "brand": "Exide", "type": "bike-battery", "capacity_ah": 9.0, "warranty_months": 48, "price": 1599.0, "description": "Reliable performance for bikes", "in_stock": True},
                {"name": "Amaron Flo 55B24L", "brand": "Amaron", "type": "car-battery", "capacity_ah": 45.0, "warranty_months": 48, "price": 5499.0, "description": "High cranking power", "in_stock": True},
                {"name": "Exide Mileage 35L", "brand": "Exide", "type": "car-battery", "capacity_ah": 35.0, "warranty_months": 44, "price": 4899.0, "description": "Long life, low maintenance", "in_stock": True},
                {"name": "Luminous Zelio+ 1100", "brand": "Luminous", "type": "inverter", "capacity_ah": None, "warranty_months": 24, "price": 6999.0, "description": "Pure sine wave inverter", "in_stock": True},
                {"name": "Luminous RC 18000", "brand": "Luminous", "type": "inverter-battery", "capacity_ah": 150.0, "warranty_months": 36, "price": 13499.0, "description": "Tubular inverter battery", "in_stock": True},
            ]
            for s in samples:
                create_document("product", s)
    except Exception:
        pass


# ---------- Models for responses ----------
class ProductsResponse(BaseModel):
    items: List[ProductSchema]
    total: int


# ---------- Routes ----------
@app.get("/")
def read_root():
    return {"shop": "Chirag Battery", "location": "Veraval, Gir Somnath", "message": "Welcome to the API"}


@app.get("/api/brands")
def get_brands():
    return {"brands": BRANDS}


@app.get("/api/types")
def get_types():
    return {"types": TYPES}


@app.get("/api/products")
def list_products(brand: Optional[str] = None, type: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    """List products with optional filters."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    filters = {}
    if brand:
        filters["brand"] = brand
    if type:
        filters["type"] = type
    if q:
        filters["name"] = {"$regex": q, "$options": "i"}

    items = get_documents("product", filters, limit)
    # Convert Mongo documents to Pydantic-friendly dicts
    for it in items:
        it.pop("_id", None)
    return {"items": items, "total": len(items)}


@app.post("/api/products", status_code=201)
def add_product(product: ProductSchema):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    _id = create_document("product", product)
    return {"id": _id, "message": "Product added"}


@app.post("/api/inquiries", status_code=201)
def create_inquiry(inquiry: InquirySchema):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    _id = create_document("inquiry", inquiry)
    return {"id": _id, "message": "Thanks! We will contact you shortly."}


@app.get("/schema")
def get_schema():
    # Expose schemas for tools/viewers if needed
    return {
        "collections": [
            {
                "name": "product",
                "fields": list(ProductSchema.model_fields.keys())
            },
            {
                "name": "inquiry",
                "fields": list(InquirySchema.model_fields.keys())
            },
        ]
    }


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
