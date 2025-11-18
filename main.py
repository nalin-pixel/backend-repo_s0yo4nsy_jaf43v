import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="Skyblock Shop API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CoinPackage(BaseModel):
    id: str
    amount_million: float = Field(..., description="Amount of coins in millions")
    price_usd: float
    description: str | None = None
    best_value: bool = False


class AccountOffer(BaseModel):
    id: str
    tier: str
    features: List[str] = []
    price_usd: float
    stock: int | None = None
    popular: bool = False


# Static demo data (no persistence required for simple pricing page)
COIN_PACKAGES: List[CoinPackage] = [
    CoinPackage(id="c1", amount_million=50, price_usd=3.99, description="Starter stack"),
    CoinPackage(id="c2", amount_million=100, price_usd=6.99, description="Good value", best_value=True),
    CoinPackage(id="c3", amount_million=250, price_usd=15.99, description="Guild grind ready"),
    CoinPackage(id="c4", amount_million=500, price_usd=28.99, description="End-game bankroll"),
]

ACCOUNT_OFFERS: List[AccountOffer] = [
    AccountOffer(
        id="a1",
        tier="Starter Account",
        features=[
            "Early-game gear",
            "Basic skills leveled",
            "Email change available",
        ],
        price_usd=14.99,
        stock=5,
    ),
    AccountOffer(
        id="a2",
        tier="Mid-Game Account",
        features=[
            "Late game gear ready",
            "Solid skill average",
            "Quality of life items",
        ],
        price_usd=34.99,
        stock=3,
        popular=True,
    ),
    AccountOffer(
        id="a3",
        tier="End-Game Account",
        features=[
            "High skill average",
            "Multiple maxed collections",
            "Slayers and dungeons progressed",
        ],
        price_usd=79.99,
        stock=2,
    ),
]


@app.get("/")
def read_root():
    return {"message": "Skyblock Shop API running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/pricing")
def get_pricing():
    return {
        "coins": [p.model_dump() for p in COIN_PACKAGES],
        "accounts": [a.model_dump() for a in ACCOUNT_OFFERS],
        "currency": "USD",
    }


@app.get("/api/pricing/coins")
def get_coins():
    return {"coins": [p.model_dump() for p in COIN_PACKAGES], "currency": "USD"}


@app.get("/api/pricing/accounts")
def get_accounts():
    return {"accounts": [a.model_dump() for a in ACCOUNT_OFFERS], "currency": "USD"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
