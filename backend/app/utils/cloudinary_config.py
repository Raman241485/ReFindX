import os
from pathlib import Path

from dotenv import load_dotenv

import cloudinary
import cloudinary.uploader


# ============================================================
# LOAD .ENV
# ============================================================

CURRENT_FILE = Path(__file__).resolve()

BACKEND_DIR = CURRENT_FILE.parents[2]

PROJECT_ROOT = CURRENT_FILE.parents[3]


# Try both locations
backend_env = BACKEND_DIR / ".env"
root_env = PROJECT_ROOT / ".env"

if backend_env.exists():
    load_dotenv(
        backend_env,
        override=True,
    )

if root_env.exists():
    load_dotenv(
        root_env,
        override=True,
    )


# ============================================================
# CLOUDINARY CONFIGURATION
# ============================================================

cloudinary.config(
    cloud_name=os.getenv(
        "CLOUDINARY_CLOUD_NAME"
    ),

    api_key=os.getenv(
        "CLOUDINARY_API_KEY"
    ),

    api_secret=os.getenv(
        "CLOUDINARY_API_SECRET"
    ),

    secure=True,
)