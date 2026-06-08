"""
FastAPI Hello World Application
Two endpoints: /health and /hello
Reads configuration from environment variables (via .env file for local dev).
"""

from fastapi import FastAPI
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Read configuration from environment with sensible defaults
SERVICE_NAME = os.getenv("SERVICE_NAME", "infra-practice-app")
VERSION = os.getenv("VERSION", "1.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
API_KEY = os.getenv("API_KEY", "default-api-key")
APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Infra Practice App",
    description="Simple FastAPI app for learning CI/CD, Docker, and Kubernetes deployment",
    version=VERSION,
)


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring, Docker health checks, and Kubernetes probes.
    Returns service status, current timestamp, and version.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat() + "Z",
        "version": VERSION,
        "environment": APP_ENV,
    }


@app.get("/hello")
def hello_world(name: str = "World"):
    """
    Hello world endpoint.
    Accepts optional 'name' query parameter.
    Example: /hello?name=Alice
    """
    return {
        "message": f"Hello, {name}!",
        "service": SERVICE_NAME,
        "version": VERSION,
    }


@app.get("/")
def root():
    """Root endpoint returns basic service info and available endpoints."""
    return {
        "service": SERVICE_NAME,
        "version": VERSION,
        "environment": APP_ENV,
        "log_level": LOG_LEVEL,
        "docs": "/docs",
        "endpoints": ["/health", "/hello", "/hello?name=YourName"],
    }


@app.get("/config")
def show_config():
    """
    Debug endpoint to verify environment variable injection.
    In production, avoid exposing secrets here.
    """
    return {
        "service_name": SERVICE_NAME,
        "version": VERSION,
        "environment": APP_ENV,
        "log_level": LOG_LEVEL,
        "api_key_loaded": bool(API_KEY and API_KEY != "default-api-key"),
    }
