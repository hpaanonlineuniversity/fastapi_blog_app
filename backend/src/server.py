# server.py (update version)
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth_route, user_route  # ✅ Add user_route
from .configs.database import get_database

environment = os.getenv("ENVIRONMENT", "development")

##app = FastAPI(title="FastAPI Auth System")

app = FastAPI(
    title="FastAPI Auth System",
    # Development မှာပဲ Swagger ဖွင့်
    docs_url="/docs" if environment != "production" else None,
    redoc_url="/redoc" if environment != "production" else None,
    
    # Production settings
    debug=False if environment == "production" else True
)

# CORS settings (same as before)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://frontend:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_route.router, prefix="/api/auth")
app.include_router(user_route.router, prefix="/api/user")  # ✅ Add this line

# Rest of the code remains the same...
@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI!"}

@app.on_event("startup")
async def startup_event():
    db = get_database()
    try:
        db.command("ping")
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )