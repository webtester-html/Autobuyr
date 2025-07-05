import asyncio
import traceback
import os
from pathlib import Path
from pyrogram import Client
from app.core.banner import display_title, get_app_info, set_window_title
from app.core.callbacks import process_gift
from app.notifications import send_start_message
from app.utils.detector import gift_monitoring
from app.utils.logger import info, error
from data.config import config, t, get_language_display

app_info = get_app_info()

class Application:
    @staticmethod
    async def run() -> None:
        set_window_title(app_info)
        display_title(app_info, get_language_display(config.LANGUAGE))

        # Check for session file in /etc/secrets
        session_path = Path('/etc/secrets/my_account.session')
        session_name = config.SESSION
        if session_path.exists():
            print(f"Using session file: {session_path}")
            async with Client(
                name=session_name,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_file=str(session_path)
            ) as client:
                await send_start_message(client)
                await gift_monitoring(client, process_gift)
        else:
            print("Session file not found, creating new session")
            async with Client(
                name=session_name,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                phone_number=config.PHONE_NUMBER
            ) as client:
                await send_start_message(client)
                await gift_monitoring(client, process_gift)

    @staticmethod
    def main() -> None:
        try:
            asyncio.run(Application.run())
        except KeyboardInterrupt:
            info(t("console.terminated"))
        except Exception:
            error(t("console.unexpected_error"))
            traceback.print_exc()

Application.main() if __name__ == "__main__" else None
