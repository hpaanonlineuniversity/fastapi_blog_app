# server.py (update version)
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth_route, user_route, post_route, comment_route, debug_route
from .configs.database import db

environment = os.getenv("ENVIRONMENT", "development")

app = FastAPI(
    title="FastAPI Auth System",
    description="Production API - Swagger disabled for security",
    version="1.0.0",
    docs_url="/docs" if environment != "production" else None,
    redoc_url="/redoc" if environment != "production" else None,
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
app.include_router(user_route.router, prefix="/api/user")
app.include_router(post_route.router, prefix="/api/post")  
app.include_router(comment_route.router, prefix="/api/comment")

app.include_router(debug_route.router, prefix="/api/debug")

# Rest of the code remains the same...
@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI!"}


# server.py (Updated startup)
@app.on_event("startup")
async def startup_event():
    # Test database connection
    try:
        await db.command("ping")
        print("✅ MongoDB connected successfully")
        
        # Connect to Redis
        from .configs.redis_client import redis_client
        await redis_client.connect()
        print("✅ Redis connected successfully")
        
        # Create admin user after successful DB connection
        from .utils.admin_setup import setup_admin_user
        await setup_admin_user()
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from Redis on shutdown"""
    from .configs.redis_client import redis_client
    await redis_client.disconnect()
    print("✅ Redis disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )