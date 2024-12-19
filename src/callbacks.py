from pyrogram import Client

import config
from src.notifications import notifications
from utils.utils import buyer

sent_gift_ids = set()


async def new_callback(app: Client, star_gift_raw: dict) -> None:
    gift_price = star_gift_raw.get("price", 0)
    locale = config.locale
    if gift_price >= config.MAX_GIFT_PRICE:
        print(
            f"\033[91m[ ! ]\033[0m {locale.gift_expensive.format(star_gift_raw['id'], gift_price)}\n"
        )
        await notifications(app, star_gift_raw['id'], gift_price=gift_price)
        return

    if star_gift_raw.get("is_limited", False):
        if star_gift_raw["id"] in sent_gift_ids:
            return
        sent_gift_ids.add(star_gift_raw["id"])

    elif config.PURCHASE_NON_LIMITED_GIFTS and gift_price <= config.MAX_GIFT_PRICE:
        if star_gift_raw["id"] not in sent_gift_ids:
            sent_gift_ids.add(star_gift_raw["id"])
    else:
        print(
            f"\033[91m[ ! ]\033[0m {locale.non_limited_gift.format(star_gift_raw['id'])}\n"
        )
        await notifications(app, star_gift_raw['id'], non_limited_error=True)
        return

    for chat_id in config.USER_ID:
        await buyer(app, chat_id, star_gift_raw["id"])


async def update_callback(app: Client, old_star_gift_raw: dict, new_gift_raw: dict) -> None:
    if "message_id" not in new_gift_raw:
        return

    message_id = new_gift_raw["message_id"]
