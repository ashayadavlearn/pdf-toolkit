import os
from pathlib import Path

# Base Directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Directory definitions
UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"
DATA_FOLDER = BASE_DIR / "data"
DATABASE_PATH = DATA_FOLDER / "toolkit.db"

# Secret Key for Flask sessions
SECRET_KEY = os.environ.get("SECRET_KEY", "pdf-toolkit-college-project-secret-key-2026")

# Security configurations
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB maximum file upload size
ALLOWED_EXTENSIONS = {"pdf"}

# Automatic directory creation
def init_directories():
    for directory in [UPLOAD_FOLDER, OUTPUT_FOLDER, DATA_FOLDER]:
        directory.mkdir(parents=True, exist_ok=True)

# Run initialization on import
init_directories()
