from pathlib import Path


# =======================
# GENERAL CONFIGURATION
# =======================
SESSION: str = str(Path(__file__).parent / "data/account")
API_ID: int = 123
API_HASH: str = "1234"


# =========================
# BOT SETTINGS
# =========================
INTERVAL: float = 5
TIMEZONE: str = "Europe/Moscow"
CHANNEL_ID: int = -000

# =========================
# FILE AND DATA PATHS
# =========================
DATA_FILEPATH: Path = Path(__file__).parent / "data/history.json"


# =========================
# GIFTS | USER INFO
# =========================
USER_ID: list[int] = [
    123, 1234
    # Be sure that both side added to contact each other
]

MAX_GIFT_PRICE = 100

PURCHASE_NON_LIMITED_GIFTS = True

HIDE_SENDER_NAME: bool = True

GIFT_IDS: list[int] = [
    # 123, 1234
    # Not necessary
]


# ========================
# Made with ❤️ by @B7XX7B
# ========================
