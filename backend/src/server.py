from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth_route
from .configs.database import get_database

app = FastAPI(title="FastAPI Auth System")

# CORS settings
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

@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI!"}

@app.on_event("startup")
async def startup_event():
    # Test database connection
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


#if you want to run fastapi from python interpreter with "python server.py" please uncomment the following codes
## or you can run with the following command
##       "uvicorn server:app --port 8000 --reload"
## if __name__ == "__main__":
##
##    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
##
##