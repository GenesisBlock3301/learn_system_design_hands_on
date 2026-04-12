"""
FastAPI Hello World Application
Two endpoints: /health and /hello
"""

from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(
    title="Infra Practice App",
    description="Simple FastAPI app for learning CI/CD and Docker deployment",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and Docker health checks.
    Returns service status, current timestamp, and version.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat() + "Z",
        "version": "1.0.0"
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
        "service": "infra-practice-app"
    }


@app.get("/")
def root():
    """Root endpoint redirects to docs or returns basic info."""
    return {
        "service": "infra-practice-app",
        "docs": "/docs",
        "endpoints": ["/health", "/hello", "/hello?name=YourName"]
    }
