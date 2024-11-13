import asyncio
import os
import sys
import traceback

import pyfiglet
from pyrogram import Client
from pyrogram.errors.exceptions import RPCError
from pytz import timezone as _timezone

import config
from src import utils
from src.callbacks import update_callback, new_callback
from src.detector import detector
from src.utils import buyer

title_text = "Gifts Buyer by @B7XX7B"
if os.name == 'nt':
    os.system(f"title {title_text}")
else:
    sys.stdout.write(f"\x1b]2;{title_text}\x07")

title = pyfiglet.figlet_format("Gifts Buyer", font="slant")
print(title.center(80))

sent_gift_ids = set()
timezone = _timezone(config.TIMEZONE)


async def main() -> None:
    app = Client(name=config.SESSION, api_id=config.API_ID, api_hash=config.API_HASH)

    await app.start()

    for gift_id in config.GIFT_IDS:
        if gift_id not in sent_gift_ids:
            for chat_id in config.USER_ID:
                try:
                    await buyer(app, chat_id, gift_id)
                    # await asyncio.sleep(3)
                except RPCError as ex:
                    print(
                        f"\n\033[91m[ ERROR ]\033[0m Error while buying a gift \033[1m{gift_id}\033[0m for user: \033[1m{chat_id}\033[0m\n{str(ex)}\n")
            sent_gift_ids.add(gift_id)

    # ========================
    # Replace the block above with this part of the code if you need to send via @username or if you have an error.
    # More details here: https://github.com/bohd4nx/TGgifts-buyer?tab=readme-ov-file#2
    # ========================

    # for gift_id in config.GIFT_IDS:
    #     if gift_id not in sent_gift_ids:
    #         for chat_id in config.USER_ID:
    #             try:
    #                 await app.send_message(chat_id, 'Hello')
    #                 await app.get_users(chat_id)
    #                 await buyer(app, chat_id, gift_id)
    #                 await asyncio.sleep(3)
    #             except RPCError as ex:
    #                 print(
    #                     f"\n\033[91m[ ERROR ]\033[0m Error while buying a gift \033[1m{gift_id}\033[0m for user: \033[1m{chat_id}\033[0m\n{str(ex)}\n")
    #         sent_gift_ids.add(gift_id)

    await detector(app, new_callback, update_callback)

    await app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        current_time = utils.current_datetime(timezone)
        print(f"\n\n\033[91m[ INFO ]\033[0m \033[1mProgram terminated\033[0m - {current_time}")
    except Exception as ex:
        print(f"\n\n\033[91m[ ERROR ]\033[0m An unexpected error occurred:")
        traceback.print_exc()  # This will print the full traceback
    finally:
        input("\n\033[91m[ INFO ]\033[0m Press \033[1mEnter\033[0m to close the program...")
