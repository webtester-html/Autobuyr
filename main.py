import asyncio
import traceback

from pyrogram import Client
from pyrogram.errors.exceptions import RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytz import timezone as _timezone

import config
from src import utils
from src.banner import title, info, cmd
from src.callbacks import update_callback, new_callback
from src.detector import detector
from src.utils import buyer

app_info = info()
cmd(app_info)
title(app_info)

sent_gift_ids = set()
timezone = _timezone(config.TIMEZONE)


async def main() -> None:
    app = Client(name=config.SESSION, api_id=config.API_ID, api_hash=config.API_HASH)

    await app.start()

    for gift_id in config.GIFT_IDS:
        if gift_id not in sent_gift_ids:
            for chat_id in config.USER_ID:
                try:
                    await app.send_message(
                        chat_id,
                        "Just a quick check-in! Feel free to ignore this message.",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton("Gifts Buyer", url="https://github.com/bohd4nx/TGgifts-buyer")]
                            ])
                    )
                    await app.get_users(chat_id)
                    await buyer(app, chat_id, gift_id)
                    await asyncio.sleep(3)
                except RPCError as ex:
                    print(
                        f"\n\033[91m[ ERROR ]\033[0m Error while buying a gift \033[1m{gift_id}\033[0m for user: \033[1m{chat_id}\033[0m\n{str(ex)}\n"
                    )
            sent_gift_ids.add(gift_id)

    await detector(app, new_callback, update_callback)

    await app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        current_time = utils.time(timezone)
        print(f"\n\n\033[91m[ INFO ]\033[0m \033[1mProgram terminated\033[0m - {current_time}")
    except Exception as ex:
        print(f"\n\n\033[91m[ ERROR ]\033[0m An unexpected error occurred:")
        traceback.print_exc()  # This will print the full traceback
    # finally:
    #     input("\n\033[91m[ INFO ]\033[0m Press \033[1mEnter\033[0m to close the program...")
