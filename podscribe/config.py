import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./podscribe.db")
WHISPERX_MODEL = os.getenv("WHISPERX_MODEL", "base")
