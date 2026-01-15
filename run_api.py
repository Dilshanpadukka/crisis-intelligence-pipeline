#!/usr/bin/env python3
"""
Startup script for Operation Ditwah Crisis Intelligence API.

Usage:
    python run_api.py                    # Development mode
    python run_api.py --env production   # Production mode
    python run_api.py --port 8080        # Custom port
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from app.config import load_config


def main():
    """Run the API server."""
    parser = argparse.ArgumentParser(
        description="Operation Ditwah Crisis Intelligence API Server"
    )
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default=None,
        help="Deployment environment"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="API host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="API port (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development only)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (production only)"
    )
    
    args = parser.parse_args()
    
    # Override environment if specified
    if args.env:
        os.environ["ENVIRONMENT"] = args.env
    
    # Load configuration
    config = load_config()
    
    # Override with command-line arguments
    host = args.host or config.api.host
    port = args.port or config.api.port
    reload = args.reload or (config.environment == "development" and config.api.reload)
    workers = args.workers or config.api.workers
    
    # Validate configuration
    if not any([
        config.llm.openai_api_key,
        config.llm.gemini_api_key,
        config.llm.groq_api_key
    ]):
        print("ERROR: No LLM API keys configured!")
        print("Please set at least one of: OPENAI_API_KEY, GEMINI_API_KEY, GROQ_API_KEY")
        print("See .env.example for configuration template")
        sys.exit(1)
    
    # Print startup information
    print("=" * 80)
    print("Operation Ditwah Crisis Intelligence API")
    print("=" * 80)
    print(f"Environment: {config.environment}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Default Provider: {config.llm.default_provider}")
    print(f"Auto-reload: {reload}")
    print(f"Workers: {workers if not reload else 1}")
    print("=" * 80)
    print(f"\nAPI Documentation: http://{host}:{port}/docs")
    print(f"ReDoc: http://{host}:{port}/redoc")
    print(f"Health Check: http://{host}:{port}/health")
    print("\nPress CTRL+C to stop the server")
    print("=" * 80)
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=1 if reload else workers,
        log_level=config.api.log_level,
        app_dir="src"
    )


if __name__ == "__main__":
    main()

