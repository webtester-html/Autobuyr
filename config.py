from pathlib import Path
from dotenv import load_dotenv
import os

# =========================
# LOAD .env VARIABLES
# =========================
load_dotenv()

# =======================
# GENERAL CONFIGURATION
# =======================
SESSION: str = str(Path(__file__).parent / "data/account")
API_ID: int = int(os.getenv("API_ID"))
API_HASH: str = os.getenv("API_HASH")
DATA_FILEPATH: Path = Path(__file__).parent / "data/history.json"

# =========================
# BOT SETTINGS
# =========================
INTERVAL: float = float(os.getenv("INTERVAL"))
TIMEZONE: str = os.getenv("TIMEZONE")
CHANNEL_ID: int = int(os.getenv("CHANNEL_ID"))

# =========================
# GIFTS | USER INFO
# =========================

# USER_ID: list[str] = list(map(str, os.getenv("USER_ID").split(',')))
# USER_ID: list[int] = list(map(int, os.getenv("USER_ID").split(',')))

USER_ID = []
user_ids = os.getenv("USER_ID", "").split(',')

for user_id in user_ids:
    try:
        USER_ID.append(int(user_id))
    except ValueError:
        USER_ID.append(user_id)

MAX_GIFT_PRICE: int = int(os.getenv("MAX_GIFT_PRICE"))
NUM_GIFTS: int = int(os.getenv("NUM_GIFTS"))

PURCHASE_NON_LIMITED_GIFTS: bool = os.getenv("PURCHASE_NON_LIMITED_GIFTS").lower() == "true"
HIDE_SENDER_NAME: bool = os.getenv("HIDE_SENDER_NAME").lower() == "true"
GIFT_IDS: list[int] = os.getenv("GIFT_IDS", "").split(",") if os.getenv("GIFT_IDS") else []
