
# ========================
# Made with ❤️ by @B7XX7B
# ========================

from pyrogram import Client

import config


async def notifications(app: Client, star_gift_id: int, gift_price: float = None,
                        user_id: int = None, username: str = None, balance_error: bool = False,
                        error_message: str = None) -> None:
    if error_message:
        message = f"<b>Error while buying a gift!</b>\n\n" \
                  f"<pre>{error_message}</pre>"
    elif balance_error:
        message = f"<b>🎁 Gift</b> [<code>{star_gift_id}</code>] could not be sent due to insufficient balance!\n" \
                  f"<b>Please top up your balance to continue sending gifts.</b>"
    elif gift_price:
        message = f"<b>🎁 Gift</b> [<code>{star_gift_id}</code>] is too expensive: <b>{gift_price} ⭐</b>. Skipping..."
    else:
        message = f"<b>🎁 Gift</b> [<code>{star_gift_id}</code>] has been successfully sent!\n\n" \
                  f"<b>Recipient:</b> @{username if username else ''} | <code>{user_id}</code>"
    try:
        await app.send_message(config.CHANNEL_ID, message.strip())
    except Exception as ex:
        print(f"\n\033[91m[ ERROR ]\033[0m Unexpected error when sending to channel: {str(ex)}")
