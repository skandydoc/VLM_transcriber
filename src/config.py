import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables
load_dotenv()

@dataclass
class AppConfig:
    """Application configuration"""
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    MAX_IMAGES: int = 100
    ALLOWED_EXTENSIONS: set = frozenset({'jpg', 'jpeg', 'png', 'webp'})
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB
    MODEL_NAME: str = "gemini-2.0-flash-exp" 