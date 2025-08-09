import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.logging import logging
from src.exception import CustomException

from src.api.api_router import api_router
# Import the MongoDB singleton to initialize it at startup
from src.db.mongodb_singleton import mongodb


app = FastAPI(title="course service apis")

# Initialize MongoDB singleton on startup
@app.on_event("startup")
async def startup_db_client():
    try:
        # The singleton is already initialized when imported
        # For Vercel, this will be called on cold starts
        logging.info("MongoDB singleton initialized successfully on startup")
    except Exception as e:
        logging.error(f"Failed to initialize MongoDB singleton: {str(e)}")
        raise e

# Error handler for serverless environment
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


# Run with hardcoded port 8080
if __name__ == "__main__":
    logging.info("Starting server at http://0.0.0.0:8080")
    # Using hardcoded port 8080
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
