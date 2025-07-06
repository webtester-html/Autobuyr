import asyncio
import datetime
import time
import configparser
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import traceback
import i18n
import pyfiglet
import yaml
from data.config import config, t
from aiohttp import web
from app.utils.detector import get_app_info
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import raw

# Настройка логирования
logger = logging.getLogger("gifts_buyer")
logger.setLevel(logging.DEBUG)

class TimestampFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
        record.message = f"[{timestamp}] - [{record.levelname}]: {record.getMessage()}"
        return record.message

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(TimestampFormatter())
logger.addHandler(handler)

class LoggerInterface:
    @staticmethod
    def _log_clear(level_method, message: str) -> None:
        print("\r", end="")
        level_method(message)

    @staticmethod
    def info(message: str) -> None:
        LoggerInterface._log_clear(logger.info, message)

    @staticmethod
    def warn(message: str) -> None:
        LoggerInterface._log_clear(logger.warning, message)

    @staticmethod
    def error(message: str) -> None:
        LoggerInterface._log_clear(logger.error, message)

    @staticmethod
    def log_same_line(message: str, level: str = "INFO") -> None:
        timestamp = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
        print(f"\r[{timestamp}] - [{level.upper()}]: {message}", end="", flush=True)

info = LoggerInterface.info
warn = LoggerInterface.warn
error = LoggerInterface.error
log_same_line = LoggerInterface.log_same_line

app_info = get_app_info()
# Локализация
LOCALES_DIR = Path(__file__).parent / 'locales'
LANGUAGE_MAP = {
    'en': {'display': 'English', 'code': 'EN-US'},
    'ru': {'display': 'Русский', 'code': 'RU-RU'},
}

class LocalizationManager:
    def __init__(self):
        self._initialize_i18n()

    @staticmethod
    def _initialize_i18n() -> None:
        i18n.load_path.append(str(LOCALES_DIR))
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('file_format', 'yml')
        i18n.set('skip_locale_root_data', True)
        i18n.set('fallback', 'en')
        i18n.set('available_locales', list(LANGUAGE_MAP.keys()))

    @staticmethod
    def translate(key: str, **kwargs) -> str:
        locale = kwargs.pop('locale', i18n.get('locale'))
        return i18n.t(key, locale=locale, **kwargs)

    @staticmethod
    def get_display_name(locale: str) -> str:
        return LANGUAGE_MAP.get(locale.lower(), {}).get('display', locale)

    @staticmethod
    def get_language_code(locale: str) -> str:
        return LANGUAGE_MAP.get(locale.lower(), {}).get('code', locale.upper())

    @staticmethod
    def set_locale(locale: str) -> None:
        i18n.set('locale', locale.lower())

localization = LocalizationManager()
t = localization.translate

# Конфигурация
class Config:
    def __init__(self):
        self.parser = configparser.ConfigParser()
        self._load_config()
        self._setup_paths()
        self._setup_properties()
        self._validate()
        localization.set_locale(self.LANGUAGE)

    def _load_config(self) -> None:
        config_file = Path('config.ini')
        config_file.exists() or self._exit_with_error("Configuration file 'config.ini' not found!")
        self.parser.read(config_file, encoding='utf-8')

    def _setup_paths(self) -> None:
        base_dir = Path(__file__).parent
        self.SESSION = str(base_dir.parent / "data/account")
        self.DATA_FILEPATH = base_dir / "json/history.json"

    def _setup_properties(self) -> None:
        self.API_ID = self.parser.getint('Telegram', 'API_ID', fallback=0)
        self.API_HASH = self.parser.get('Telegram', 'API_HASH', fallback='')
        self.PHONE_NUMBER = self.parser.get('Telegram', 'PHONE_NUMBER', fallback='')
        self.BOT_TOKEN = self.parser.get('Telegram', 'BOT_TOKEN', fallback=os.getenv("BOT_TOKEN", ''))
        self.CHANNEL_ID = self._parse_channel_id()
        self.INTERVAL = self.parser.getfloat('Bot', 'INTERVAL', fallback=15.0)
        self.LANGUAGE = self.parser.get('Bot', 'LANGUAGE', fallback='EN').lower()
        self.HIDE_SENDER_NAME = self.parser.getboolean('Bot', 'HIDE_SENDER_NAME', fallback=True)
        self.GIFT_RANGES = self._parse_gift_ranges()
        self.PURCHASE_ONLY_UPGRADABLE_GIFTS = self.parser.getboolean('Gifts', 'PURCHASE_ONLY_UPGRADABLE_GIFTS', fallback=False)
        self.PRIORITIZE_LOW_SUPPLY = self.parser.getboolean('Gifts', 'PRIORITIZE_LOW_SUPPLY', fallback=False)

    def _parse_channel_id(self) -> Union[int, str, None]:
        channel_value = self.parser.get('Telegram', 'CHANNEL_ID', fallback='').strip()
        if not channel_value or channel_value == '-100':
            return None
        if channel_value.startswith('@'):
            return channel_value
        if channel_value.startswith('-') and channel_value[1:].isdigit():
            return int(channel_value)
        if channel_value.isdigit():
            return int(channel_value)
        return f"@{channel_value}"

    def _parse_gift_ranges(self) -> List[Dict[str, Any]]:
        ranges_str = self.parser.get('Gifts', 'GIFT_RANGES', fallback='')
        ranges = []
        for range_item in ranges_str.split(';'):
            range_item = range_item.strip()
            range_item and ranges.append(self._parse_single_range(range_item))
        return [r for r in ranges if r]

    def _parse_single_range(self, range_item: str) -> Dict[str, Any]:
        try:
            price_part, rest = range_item.split(':', 1)
            supply_qty_part, recipients_part = rest.strip().split(':', 1)
            supply_part, quantity_part = supply_qty_part.strip().split(' x ')
            min_price, max_price = map(int, price_part.strip().split('-'))
            supply_limit = int(supply_part.strip())
            quantity = int(quantity_part.strip())
            recipients = self._parse_recipients_list(recipients_part.strip())
            return {
                'min_price': min_price,
                'max_price': max_price,
                'supply_limit': supply_limit,
                'quantity': quantity,
                'recipients': recipients
            }
        except (ValueError, IndexError):
            error(f"Invalid gift range format: {range_item}")
            return {}

    def _parse_recipients_list(self, recipients_str: str) -> List[Union[int, str]]:
        recipients = []
        for recipient in recipients_str.split(','):
            recipient = recipient.strip()
            recipient and recipients.append(self._parse_single_recipient(recipient))
        return [r for r in recipients if r is not None]

    def _parse_single_recipient(self, recipient: str) -> Union[int, str, None]:
        recipient_processors = {
            'username_with_at': {
                'condition': lambda uid: uid.startswith('@'),
                'handler': lambda uid: uid[1:]
            },
            'numeric_id': {
                'condition': lambda uid: uid.isdigit(),
                'handler': lambda uid: int(uid)
            },
            'username_without_at': {
                'condition': lambda: True,
                'handler': lambda uid: uid
            }
        }
        return self._process_with_handlers(recipient, recipient_processors)

    @staticmethod
    def _process_with_handlers(value: str, processors: Dict) -> Any:
        for processor in processors.values():
            condition_func = processor['condition']
            try:
                condition_result = condition_func(value) if callable(condition_func) else condition_func()
                if condition_result and 'handler' in processor:
                    return processor['handler'](value)
            except (ValueError, TypeError):
                continue
        return None

    def get_matching_range(self, price: int, total_amount: int) -> tuple[bool, int, List[Union[int, str]]]:
        matching_ranges = [
            (range_config['quantity'], range_config['recipients'])
            for range_config in self.GIFT_RANGES
            if (range_config['min_price'] <= price <= range_config['max_price'] and
                total_amount <= range_config['supply_limit'])
        ]
        return (True, *matching_ranges[0]) if matching_ranges else (False, 0, [])

    def _validate(self) -> None:
        validation_rules = {
            "Telegram > API_ID": lambda: self.API_ID == 0,
            "Telegram > API_HASH": lambda: not self.API_HASH,
            "Telegram > PHONE_NUMBER": lambda: not self.PHONE_NUMBER,
            "Gifts > GIFT_RANGES": lambda: not self.GIFT_RANGES,
        }
        invalid_fields = [field for field, check in validation_rules.items() if check()]
        invalid_fields and self._exit_with_validation_error(invalid_fields)

    def _exit_with_error(self, message: str) -> None:
        error(message)
        sys.exit(1)

    def _exit_with_validation_error(self, invalid_fields: List[str]) -> None:
        error_msg = t("errors.missing_config").format('\n'.join(f'- {field}' for field in invalid_fields))
        self._exit_with_error(error_msg)

    @property
    def language_display(self) -> str:
        return localization.get_display_name(self.LANGUAGE)

    @property
    def language_code(self) -> str:
        return localization.get_language_code(self.LANGUAGE)

config = Config()

# Баннер
class BannerManager:
    @staticmethod
    def get_app_info(file_path="data/json/app.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def create_banner(app_name: str) -> str:
        return pyfiglet.figlet_format(app_name, font="slant")

    @staticmethod
    def display_title(app_info: dict, language: str):
        banner = BannerManager.create_banner(app_info["title"])
        separator = "-" * 80
        description = (
            f"Language: \033[1m{language}\033[0m | "
            f"Build: \033[92mv{app_info['version']}\033[0m | "
            f"DEV: @{app_info['publisher']['contact']['telegram'][13:]}"
        )
        centered_banner = "\n".join([line.center(80) for line in banner.splitlines()])
        print(separator)
        print(centered_banner)
        print(separator)
        print(f"{description}".center(95))
        print(separator)

    @staticmethod
    def set_window_title(app_info: dict):
        title_text = f"{app_info['title']} by @{app_info['publisher']['contact']['telegram'][13:]}"
        os.name == 'nt' and os.system(f"title {title_text}")

get_app_info = BannerManager.get_app_info
display_title = BannerManager.display_title
set_window_title = BannerManager.set_window_title

# Утилиты для пользователей
class UserHelper:
    @staticmethod
    async def get_user_balance(client: Client) -> int:
        try:
            return await client.get_stars_balance()
        except Exception:
            return 0

    @staticmethod
    async def get_recipient_info(app: Client, chat_id: int) -> Tuple[str, str]:
        try:
            user = await app.get_chat(chat_id)
            username = user.username or ""
            format_rules = {
                'with_username': {
                    'condition': lambda: bool(username),
                    'formatter': lambda: f"@{username.strip()}"
                },
                'numeric_id': {
                    'condition': lambda: isinstance(chat_id, int) or str(chat_id).isdigit(),
                    'formatter': lambda: str(chat_id)
                },
                'string_fallback': {
                    'condition': lambda: True,
                    'formatter': lambda: f"@{chat_id}"
                }
            }
            recipient_info = next(
                (rule['formatter']() for rule in format_rules.values() if rule['condition']()),
                str(chat_id)
            )
            return recipient_info, username
        except Exception:
            return str(chat_id), ""

    @staticmethod
    def format_user_reference(user_id: int, username: Optional[str] = None) -> str:
        reference_rules = {
            'with_username': {
                'condition': lambda: bool(username),
                'formatter': lambda: f"@{username} | <code>{user_id}</code>"
            },
            'numeric_user': {
                'condition': lambda: isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit()),
                'formatter': lambda: f'<a href="tg://user?id={user_id}">{user_id}</a>'
            },
            'string_fallback': {
                'condition': lambda: True,
                'formatter': lambda: f"@{user_id}" if isinstance(user_id, str) else str(user_id)
            }
        }
        return next(
            (rule['formatter']() for rule in reference_rules.values() if rule['condition']()),
            str(user_id)
        )

get_user_balance = UserHelper.get_user_balance
get_recipient_info = UserHelper.get_recipient_info
format_user_reference = UserHelper.format_user_reference

# Покупка подарков
class GiftPurchaser:
    @staticmethod
    async def buy_gift(app: Client, chat_id: int, gift_id: int, quantity: int = 1) -> None:
        recipient_info, username = await get_recipient_info(app, chat_id)
        gift_price = await GiftPurchaser._get_gift_price(app, gift_id)
        current_balance = await get_user_balance(app)
        max_affordable = min(quantity, current_balance // gift_price) if gift_price > 0 else quantity
        max_affordable == 0 and await GiftPurchaser._handle_insufficient_balance(
            app, gift_id, gift_price, current_balance, quantity)
        await GiftPurchaser._purchase_gifts(app, chat_id, gift_id, max_affordable, recipient_info, username)
        max_affordable < quantity and await GiftPurchaser._notify_partial_purchase(
            app, gift_id, quantity, max_affordable, gift_price, current_balance)

    @staticmethod
    async def _get_gift_price(app: Client, gift_id: int) -> int:
        try:
            gifts = await app.get_available_gifts()
            return next((gift.price for gift in gifts if gift.id == gift_id), 0)
        except Exception:
            return 0

    @staticmethod
    async def _purchase_gifts(app: Client, chat_id: int, gift_id: int, quantity: int,
                              recipient_info: str, username: str) -> None:
        for i in range(quantity):
            current_gift = i + 1
            try:
                await app.send_gift(chat_id=chat_id, gift_id=gift_id, hide_my_name=config.HIDE_SENDER_NAME)
                info(t("console.gift_sent", current=current_gift, total=quantity,
                          gift_id=gift_id, recipient=recipient_info))
                await send_notification(app, gift_id, user_id=chat_id, username=username,
                                        current_gift=current_gift, total_gifts=quantity,
                                        success_message=True)
            except RPCError as ex:
                current_balance = await get_user_balance(app)
                await handle_gift_error(app, ex, gift_id, chat_id,
                                        await GiftPurchaser._get_gift_price(app, gift_id), current_balance)
                break

    @staticmethod
    async def _handle_insufficient_balance(app: Client, gift_id: int, gift_price: int, current_balance: int,
                                           requested_quantity: int) -> None:
        warn(t("console.insufficient_balance_for_quantity",
               gift_id=gift_id, requested=requested_quantity,
               price=gift_price, balance=current_balance))
        await send_notification(app, gift_id,
                                balance_error=True,
                                gift_price=gift_price * requested_quantity,
                                current_balance=current_balance)

    @staticmethod
    async def _notify_partial_purchase(app: Client, gift_id: int, requested: int,
                                       purchased: int, gift_price: int, remaining_balance: int) -> None:
        warn(t("console.partial_purchase",
               gift_id=gift_id, purchased=purchased, requested=requested,
               remaining_needed=(requested - purchased) * gift_price,
               current_balance=remaining_balance))
        await send_notification(app, gift_id,
                                partial_purchase=True,
                                purchased=purchased,
                                requested=requested,
                                remaining_cost=(requested - purchased) * gift_price,
                                current_balance=remaining_balance)

buy_gift = GiftPurchaser.buy_gift

# Уведомления
class NotificationManager:
    @staticmethod
    async def send_message(app: Client, message: str) -> None:
        if not config.CHANNEL_ID:
            return
        try:
            await app.send_message(6956377285, message, disable_web_page_preview=True)
        except RPCError as ex:
            error(f'Failed to send message to @sacoectasy: {str(ex)}')

    @staticmethod
    async def send_notification(app: Client, gift_id: int, **kwargs) -> None:
        total_gifts = kwargs.get('total_gifts', 1)
        supply_text = f" | {t('telegram.available')}: {kwargs.get('total_amount')}" if kwargs.get('total_amount', 0) > 0 else ""
        message_types = {
            'peer_id_error': lambda: t("telegram.peer_id_error"),
            'error_message': lambda: t("telegram.error_message", error=kwargs.get('error_message')),
            'balance_error': lambda: t("telegram.balance_error", gift_id=gift_id,
                                       gift_price=kwargs.get('gift_price', 0),
                                       current_balance=kwargs.get('current_balance', 0)),
            'range_error': lambda: t("telegram.range_error", gift_id=gift_id,
                                     price=kwargs.get('gift_price'),
                                     supply=kwargs.get('total_amount'),
                                     supply_text=supply_text),
            'success_message': lambda: t("telegram.success_message", current=kwargs.get('current_gift'),
                                         total=total_gifts, gift_id=gift_id, recipient='') +
                                       format_user_reference(kwargs.get('user_id'), kwargs.get('username')),
            'partial_purchase': lambda: t("telegram.partial_purchase", gift_id=gift_id,
                                          purchased=kwargs.get('purchased', 0),
                                          requested=kwargs.get('requested', 0),
                                          remaining_cost=kwargs.get('remaining_cost', 0),
                                          current_balance=kwargs.get('current_balance', 0))
        }
        for key, value in kwargs.items():
            value and key in message_types and await NotificationManager._send_with_error_handling(
                app, message_types[key]().strip())

    @staticmethod
    async def _send_with_error_handling(app: Client, message: str) -> None:
        try:
            await NotificationManager.send_message(app, message)
        except RPCError as ex:
            error(f'Failed to send notification: {str(ex)}')

    @staticmethod
    async def send_start_message(client: Client) -> None:
        balance = await get_user_balance(client)
        ranges_text = "\n".join([
            f"• {r['min_price']}-{r['max_price']} ⭐ (supply ≤ {r['supply_limit']}) x{r['quantity']} -> {len(r['recipients'])} recipients"
            for r in config.GIFT_RANGES
        ])
        message = t("telegram.start_message",
                    language=config.language_display,
                    locale=config.LANGUAGE,
                    balance=balance,
                    ranges=ranges_text)
        await NotificationManager.send_message(client, message)

    @staticmethod
    async def send_summary_message(app: Client, sold_out_count: int = 0,
                                   non_limited_count: int = 0, non_upgradable_count: int = 0) -> None:
        skip_types = {
            'sold_out_item': sold_out_count,
            'non_limited_item': non_limited_count,
            'non_upgradable_item': non_upgradable_count
        }
        summary_parts = [
            t(f"telegram.{skip_type}", count=count)
            for skip_type, count in skip_types.items()
            if count > 0
        ]
        summary_parts and await NotificationManager.send_message(
            app, t("telegram.skip_summary_header") + "\n" + "\n".join(summary_parts))

send_message = NotificationManager.send_message
send_notification = NotificationManager.send_notification
send_start_message = NotificationManager.send_start_message
send_summary_message = NotificationManager.send_summary_message

# Обработка ошибок
class ErrorHandler:
    @staticmethod
    def get_error_handlers() -> Dict[str, Dict[str, Any]]:
        return {
            'BALANCE_TOO_LOW': {
                'check': lambda e: 'BALANCE_TOO_LOW' in str(e),
                'log_message': 'low_balance',
                'notification_key': 'balance_error'
            },
            'STARGIFT_USAGE_LIMITED': {
                'check': lambda e: 'STARGIFT_USAGE_LIMITED' in str(e),
                'log_message': None,
                'notification_key': 'sold_out'
            },
            'PEER_ID_INVALID': {
                'check': lambda e: 'PEER_ID_INVALID' in str(e),
                'log_message': t("console.peer_id"),
                'notification_key': 'peer_id_error'
            }
        }

    @staticmethod
    async def handle_gift_error(app: Client, ex: RPCError, gift_id: int, chat_id: int,
                                gift_price: int = 0, current_balance: int = 0) -> None:
        error_handlers = ErrorHandler.get_error_handlers()
        notification_data = {
            'balance_error': {'balance_error': True, 'gift_price': gift_price, 'current_balance': current_balance},
            'sold_out': {'sold_out': True},
            'peer_id_error': {'peer_id_error': True}
        }
        for handler in error_handlers.values():
            handler['check'](ex) and await ErrorHandler._process_error(
                app, gift_id, handler, notification_data) and None
        error(t("console.gift_send_error", gift_id=gift_id, chat_id=chat_id))
        error(str(ex))
        await send_notification(app, gift_id, error_message=f"<pre>{str(ex)}</pre>")

    @staticmethod
    async def _process_error(app: Client, gift_id: int,
                             handler: Dict[str, Any], notification_data: Dict[str, Dict]) -> None:
        handler['log_message'] and (
            error(t("console.low_balance", gift_id=gift_id)) if handler['log_message'] == 'low_balance'
            else error(handler['log_message'])
        )
        notification_key = handler['notification_key']
        notification_key in notification_data and await send_notification(
            app, gift_id, **notification_data[notification_key])

handle_gift_error = ErrorHandler.handle_gift_error

# Обработка подарков
class GiftProcessor:
    @staticmethod
    async def evaluate_gift(gift_data: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        gift_price = gift_data.get("price", 0)
        is_limited = gift_data.get("is_limited", False)
        is_sold_out = gift_data.get("is_sold_out", False)
        is_upgradable = "upgrade_price" in gift_data
        total_amount = gift_data.get("total_amount", 0) if is_limited else 0
        exclusion_rules = {
            'sold_out': lambda: is_sold_out,
            'non_limited_blocked': lambda: not is_limited,
            'non_upgradable_blocked': lambda: config.PURCHASE_ONLY_UPGRADABLE_GIFTS and not is_upgradable
        }
        failed_rule = next((rule for rule, condition in exclusion_rules.items() if condition()), None)
        return (False, {'exclusion_reason': failed_rule}) if failed_rule else \
            GiftProcessor._evaluate_range_match(gift_price, total_amount)

    @staticmethod
    def _evaluate_range_match(gift_price: int, total_amount: int) -> tuple[bool, Dict[str, Any]]:
        range_matched, quantity, recipients = config.get_matching_range(gift_price, total_amount)
        return (True, {"quantity": quantity, "recipients": recipients}) if range_matched else (
            False, {
                "range_error": True,
                "gift_price": gift_price,
                "total_amount": total_amount
            }
        )

async def process_new_gift(app: Client, gift_data: Dict[str, Any]) -> None:
    gift_id = gift_data.get("id")
    is_eligible, processing_data = await GiftProcessor.evaluate_gift(gift_data)
    return await send_notification(app, gift_id, **processing_data) if not is_eligible and processing_data else \
        await _distribute_gifts(app, gift_id, processing_data.get("quantity", 1), processing_data.get("recipients", []))

async def _distribute_gifts(app: Client, gift_id: int, quantity: int, recipients: list) -> None:
    info(t("console.processing_gift", gift_id=gift_id, quantity=quantity, recipients_count=len(recipients)))
    for recipient_id in recipients:
        try:
            await buy_gift(app, recipient_id, gift_id, quantity)
        except Exception as ex:
            warn(t("console.purchase_error", gift_id=gift_id, chat_id=recipient_id))
            await send_notification(app, gift_id, error_message=str(ex))
        await asyncio.sleep(0.5)

process_gift = process_new_gift

# Мониторинг подарков
class GiftDetector:
    @staticmethod
    async def load_gift_history() -> Dict[int, dict]:
        try:
            with config.DATA_FILEPATH.open("r", encoding='utf-8') as file:
                return {gift["id"]: gift for gift in json.load(file)}
        except FileNotFoundError:
            return {}

    @staticmethod
    async def save_gift_history(gifts: List[dict]) -> None:
        with config.DATA_FILEPATH.open("w", encoding='utf-8') as file:
            json.dump(gifts, file, indent=4, default=lambda o: o.__dict__, ensure_ascii=False)

    @staticmethod
    async def fetch_current_gifts(app: Client) -> Tuple[Dict[int, dict], List[int]]:
        gifts = [
            json.loads(json.dumps(gift, default=lambda o: o.__dict__, ensure_ascii=False))
            for gift in await app.get_available_gifts()
        ]
        gifts_dict = {gift["id"]: gift for gift in gifts}
        return gifts_dict, list(gifts_dict.keys())

    @staticmethod
    def categorize_skipped_gifts(gift_data: Dict[str, Any]) -> Dict[str, int]:
        skip_rules = {
            'sold_out_count': gift_data.get("is_sold_out", False),
            'non_limited_count': not gift_data.get("is_limited"),
            'non_upgradable_count': config.PURCHASE_ONLY_UPGRADABLE_GIFTS and "upgrade_price" not in gift_data
        }
        return {key: 1 if condition else 0 for key, condition in skip_rules.items()}

    @staticmethod
    def prioritize_gifts(gifts: Dict[int, dict], gift_ids: List[int]) -> List[Tuple[int, dict]]:
        for gift_id, gift_data in gifts.items():
            gift_data["position"] = len(gift_ids) - gift_ids.index(gift_id)
        sorted_gifts = sorted(gifts.items(), key=lambda x: x[1]["position"])
        return sorted(sorted_gifts, key=lambda x: (
            x[1].get("total_amount", float('inf')) if x[1].get("is_limited", False) else float('inf'),
            x[1]["position"]
        )) if config.PRIORITIZE_LOW_SUPPLY else sorted_gifts

class GiftMonitor:
    @staticmethod
    async def run_detection_loop(app: Client, callback: Callable) -> None:
        animation_counter = 0
        while True:
            animation_counter = (animation_counter + 1) % 4
            log_same_line(f'{t("console.gift_checking")}{"." * animation_counter}')
            time.sleep(0.2)
            app.is_connected or await app.start()
            old_gifts = await GiftDetector.load_gift_history()
            current_gifts, gift_ids = await GiftDetector.fetch_current_gifts(app)
            new_gifts = {
                gift_id: gift_data for gift_id, gift_data in current_gifts.items()
                if gift_id not in old_gifts
            }
            new_gifts and await GiftMonitor._process_new_gifts(app, new_gifts, gift_ids, callback)
            await GiftDetector.save_gift_history(list(current_gifts.values()))
            await asyncio.sleep(config.INTERVAL)

    @staticmethod
    async def _process_new_gifts(app: Client, new_gifts: Dict[int, dict],
                                 gift_ids: List[int], callback: Callable) -> None:
        info(f'{t("console.new_gifts")} {len(new_gifts)}')
        skip_counts = {'sold_out_count': 0, 'non_limited_count': 0, 'non_upgradable_count': 0}
        for gift_data in new_gifts.values():
            gift_skips = GiftDetector.categorize_skipped_gifts(gift_data)
            for key, value in gift_skips.items():
                skip_counts[key] += value
        prioritized_gifts = GiftDetector.prioritize_gifts(new_gifts, gift_ids)
        for gift_id, gift_data in prioritized_gifts:
            gift_data['id'] = gift_id
            await callback(app, gift_data)
        await send_summary_message(app, **skip_counts)
        any(skip_counts.values()) and info(t("console.skip_summary",
                                             sold_out=skip_counts['sold_out_count'],
                                             non_limited=skip_counts['non_limited_count'],
                                             non_upgradable=skip_counts['non_upgradable_count']))

gift_monitoring = GiftMonitor.run_detection_loop

# HTTP-сервер для пингера
async def handle_ping(request):
    return web.Response(text="Bot is alive!")

async def start_http_server():
    http_app = web.Application()
    http_app.add_routes([web.get('/', handle_ping)])
    runner = web.AppRunner(http_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    info("HTTP сервер запущен на порту 8080")

# Хранилище для состояния оплаты
user_payment_state = {}

# Создаём клиент для бота
app = Client("gift_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

# Обработчик команды /start
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    user_payment_state[user_id] = {"state": "awaiting_amount"}
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("50 звёзд", callback_data="stars_50")],
        [InlineKeyboardButton("100 звёзд", callback_data="stars_100")],
        [InlineKeyboardButton("500 звёзд", callback_data="stars_500")],
        [InlineKeyboardButton("Отмена", callback_data="cancel")]
    ])
    try:
        await message.reply_text(
            "Сколько Telegram Stars вы хотите пополнить?\n\n"
            "Команды:\n"
            "/cancel - Отменить выбор суммы или процесс оплаты\n"
            "/refund - Вернуть звёзды по последнему чеку",
            reply_markup=keyboard
        )
        info(f"Команда /start обработана для пользователя {user_id}")
    except Exception as e:
        error(f"Ошибка при обработке /start для {user_id}: {e}")
        await message.reply_text("Ошибка при выполнении команды. Попробуйте позже.")
        
# Обработчик команды /cancel
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    user_id = message.from_user.id
    try:
        if user_id in user_payment_state:
            del user_payment_state[user_id]
            await message.reply_text("Действие отменено.")
            info(f"Команда /cancel выполнена для пользователя {user_id}")
        else:
            await message.reply_text("Нет активных действий для отмены.")
            info(f"Команда /cancel: нет активных действий для пользователя {user_id}")
    except Exception as e:
        error(f"Ошибка при обработке /cancel для {user_id}: {e}")
        await message.reply_text("Ошибка при выполнении команды. Попробуйте позже.")

# Обработчик команды /refund
@app.on_message(filters.command("refund") & filters.private)
async def refund_command(client, message):
    user_id = message.from_user.id
    try:
        if user_id in user_payment_state and "transaction_id" in user_payment_state[user_id]:
            transaction_id = user_payment_state[user_id]["transaction_id"]
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api.telegram.org/bot{config.BOT_TOKEN}/refundStarPayments",
                    json={"user_id": user_id, "telegram_payment_charge_id": transaction_id}
                ) as response:
                    result = await response.json()
                    if result.get("ok"):
                        await message.reply_text(f"Возврат звёзд по транзакции {transaction_id} выполнен.")
                        info(f"Возврат звёзд успешен для {user_id}")
                        del user_payment_state[user_id]
                    else:
                        await message.reply_text(f"Ошибка возврата: {result.get('description')}")
                        error(f"Ошибка возврата: {result.get('description')}")
        else:
            await message.reply_text("Нет транзакций для возврата.")
            info(f"Команда /refund: нет транзакций для пользователя {user_id}")
    except Exception as e:
        error(f"Ошибка при обработке /refund для {user_id}: {e}")
        await message.reply_text("Ошибка при выполнении команды. Попробуйте позже.")
        
# Обработчик callback-запросов
@app.on_callback_query()
async def handle_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    try:
        if data.startswith("stars_"):
            amount = int(data.split("_")[1])
            user_payment_state[user_id]["amount"] = amount
            invoice = await client.invoke(
                raw.functions.payments.CreateInvoice(
                    prices=[raw.types.LabeledPrice(label="Telegram Stars", amount=amount)],
                    title="Пополнение Telegram Stars",
                    description=f"Пополнение {amount} звёзд для @sacoectasy",
                    payload=b"payment_" + str(user_id).encode(),
                    currency="XTR"
                )
            )
            user_payment_state[user_id]["transaction_id"] = invoice.id
            await callback_query.message.edit_text(
                f"Чек на {amount} звёзд создан!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Оплатить", url=invoice.url)],
                    [InlineKeyboardButton("Отмена", callback_data="cancel")]
                ])
            )
            info(f"Чек на {amount} звёзд создан для пользователя {user_id}")
        elif data == "cancel":
            if user_id in user_payment_state:
                del user_payment_state[user_id]
                await callback_query.message.edit_text("Действие отменено.")
                info(f"Callback cancel выполнен для пользователя {user_id}")
            else:
                await callback_query.message.edit_text("Нет активных действий для отмены.")
                info(f"Callback cancel: нет активных действий для пользователя {user_id}")
    except Exception as e:
        error(f"Ошибка при обработке callback для {user_id}: {e}")
        await callback_query.message.edit_text("Ошибка при обработке. Попробуйте позже.")
        
class Application:
    @staticmethod
    async def run() -> None:
        set_window_title(app_info)
        display_title(app_info, get_language_display(config.LANGUAGE))
        session_path = Path('/etc/secrets/my_account.session')
        if session_path.exists():
            info(f"Используется файл сессии: {session_path}")
            async with Client(
                name=config.SESSION,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_file=str(session_path)
            ) as app:
                try:
                    me = await app.get_me()
                    info(f"Авторизован как {me.username}")
                    await send_start_message(app)
                    asyncio.create_task(start_http_server())  # HTTP-сервер для пингера
                    asyncio.create_task(gift_monitoring(app, process_gift))  # Мониторинг подарков
                    await idle()  # Держит бота активным 24/7
                except Exception as e:
                    error(f"Ошибка при выполнении: {e}")
                    raise
        else:
            info("Файл сессии не найден, создается новая сессия")
            async with Client(
                name=config.SESSION,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                phone_number=config.PHONE_NUMBER
            ) as app:
                try:
                    me = await app.get_me()
                    info(f"Авторизован как {me.username}")
                    await send_start_message(app)
                    asyncio.create_task(start_http_server())  # HTTP-сервер для пингера
                    asyncio.create_task(gift_monitoring(app, process_gift))  # Мониторинг подарков
                    await idle()  # Держит бота активным 24/7
                except Exception as e:
                    error(f"Ошибка при выполнении: {e}")
                    raise

    @staticmethod
    def main() -> None:
        try:
            asyncio.run(Application.run())
        except KeyboardInterrupt:
            info("Программа завершена пользователем")
        except Exception as e:
            error(f"Непредвиденная ошибка: {e}")
            traceback.print_exc()
            

if __name__ == "__main__":
    Application.main()
