
# ========================
# Made with ❤️ by @B7XX7B
# ========================

import asyncio

import pyfiglet
from pyrogram import Client
from pyrogram.errors.exceptions import RPCError
from pytz import timezone as _timezone

import config
from src.callbacks import update_callback, new_callback
from src.detector import detector
from src.utils import buyer

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
                except RPCError as ex:
                    print(
                        f"\n\033[91m[ ERROR ]\033[0m Error while buying a gift \033[1m{gift_id}\033[0m for user: \033[1m{chat_id}\033[0m\n{str(ex)}\n")
            sent_gift_ids.add(gift_id)

            #     except RPCError as ex:
            #         error_message = (
            #             f"<b>Error</b> while buying a gift for <code>{chat_id}</code>\n"
            #             f"<pre>{str(ex)}</pre>"
            #         )
            #         print(
            #             f"\n\033[91m[ ERROR ]\033[0m Error while buying a gift \033[1m{gift_id}\033[0m "
            #             f"to \033[1m{chat_id}\033[0m\n{str(ex)}"
            #         )
            #         await notifications(
            #             app,
            #             gift_id,
            #             error_message=error_message
            #         )
            # sent_gift_ids.add(gift_id)

    await detector(app, new_callback, update_callback)

    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
