from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.endpoints import router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Student Credit FastAPI Server", 
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "chat": "/api/v1/chat",
            "debate_loan": "/api/v1/debate-loan"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)