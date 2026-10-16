"""
Vercel Serverless Function Entrypoint for NutriSphere X (FastAPI backend).
This module initializes the FastAPI application instance for Vercel's Python runtime.
"""

import sys
import os
from pathlib import Path

# Mark environment as Vercel
os.environ["VERCEL"] = "1"

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the initialized FastAPI app
from backend.main import app
