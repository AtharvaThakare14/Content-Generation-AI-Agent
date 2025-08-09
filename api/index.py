from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add the root directory to Python path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the application from main
from main import app as main_app

# Create a handler for serverless environments
async def handler(request: Request):
    return await main_app(request.scope, request.receive, request.send)

# Export for Vercel serverless
app = main_app
