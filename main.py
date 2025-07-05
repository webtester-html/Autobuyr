import asyncio
import traceback
import configparser
import logging
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Чтение конфига
config = configparser.ConfigParser()
try:
    if not config.read('config.ini'):
        logging.error("Файл config.ini не найден или пуст")
        raise FileNotFoundError("config.ini не найден")
    logging.info("Файл config.ini успешно прочитан")
except Exception as e:
    logging.error(f"Ошибка чтения config.ini: {e}")
    raise

# Параметры из конфига
try:
    API_ID = int(config['Telegram']['API_ID'])  # 24122577
    API_HASH = config['Telegram']['API_HASH']   # 428513682803fb9f74a7754aafdd38ce
    BOT_TOKEN = config['Telegram']['BOT_TOKEN']  # Токен бота от @BotFather
    CHANNEL_ID = config['Telegram']['CHANNEL_ID']  # -100
    INTERVAL = int(config['Bot']['INTERVAL'])  # 10
    LANGUAGE = config['Bot']['LANGUAGE']  # RU
    HIDE_SENDER_NAME = config['Bot']['HIDE_SENDER_NAME'].lower() == 'true'  # True
    GIFT_RANGES = config['Gifts']['GIFT_RANGES']  # 1-1000: 500000 x 5: @sacoectasy, 6956377285;
    PURCHASE_ONLY_UPGRADABLE_GIFTS = config['Gifts']['PURCHASE_ONLY_UPGRADABLE_GIFTS'].lower() == 'true'  # False
    PRIORITIZE_LOW_SUPPLY = config['Gifts']['PRIORITIZE_LOW_SUPPLY'].lower() == 'true'  # True
    logging.info("Все параметры из config.ini успешно загружены")
except KeyError as e:
    logging.error(f"Отсутствует параметр в config.ini: {e}")
    raise
except Exception as e:
    logging.error(f"Ошибка при чтении параметров из config.ini: {e}")
    raise

# Заглушка для отсутствующих модулей
def display_title(app_info, language): logging.info(f"Заглушка: display_title({app_info}, {language})")
def get_app_info(): return {"name": "GiftBot", "version": "1.0"}
def set_window_title(app_info): logging.info(f"Заглушка: set_window_title({app_info})")

# Создаём клиент для бота
app = Client("gift_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Хранилище для состояния оплаты (временное, для примера)
user_payment_state = {}

async def send_start_message(client): 
    await client.send_message(6956377285, "Бот запущен на Render!")
    logging.info("Тестовое сообщение отправлено пользователю @sacoectasy")

async def gift_monitoring(client, callback): 
    logging.info("Запущен мониторинг подарков")
    while True:
        try:
            # Заглушка: здесь должна быть реальная логика мониторинга подарков
            # Предположим, что бот обнаруживает новый подарок
            new_gift = {"name": "Example Gift", "price": 100}  # Пример подарка
            await callback(client, new_gift)
            await asyncio.sleep(INTERVAL)  # Периодичность проверки (10 секунд)
        except Exception as e:
            logging.error(f"Ошибка в gift_monitoring: {e}")
            await asyncio.sleep(INTERVAL)

async def process_gift(client, gift): 
    # Уведомление о новом подарке пользователю @sacoectasy
    message = f"Обнаружен новый подарок: {gift['name']} за {gift['price']} звёзд!"
    await client.send_message(6956377285, message)
    logging.info(f"Уведомление о подарке отправлено: {message}")

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
    await message.reply_text(
        "Сколько Telegram Stars вы хотите пополнить?\n\n"
        "Команды:\n"
        "/cancel - Отменить выбор суммы\n"
        "/refund - Вернуть звёзды по последнему чеку",
        reply_markup=keyboard
    )
    logging.info(f"Команда /start обработана для пользователя {user_id}")

# Обработчик команды /cancel
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    user_id = message.from_user.id
    if user_id in user_payment_state:
        del user_payment_state[user_id]
        await message.reply_text("Действие отменено.")
        logging.info(f"Команда /cancel выполнена для пользователя {user_id}")
    else:
        await message.reply_text("Нет активных действий для отмены.")
        logging.info(f"Команда /cancel: нет активных действий для пользователя {user_id}")

# Обработчик команды /refund
@app.on_message(filters.command("refund") & filters.private)
async def refund_command(client, message):
    user_id = message.from_user.id
    if user_id in user_payment_state and "transaction_id" in user_payment_state[user_id]:
        transaction_id = user_payment_state[user_id]["transaction_id"]
        try:
            # Метод для возврата звёзд (Pyrogram пока не поддерживает нативно, нужен обход)
            # Здесь должен быть вызов Telegram Bot API через HTTP-запрос
            await message.reply_text(f"Возврат звёзд по транзакции {transaction_id} инициирован.")
            logging.info(f"Команда /refund выполнена для транзакции {transaction_id}")
            del user_payment_state[user_id]
        except Exception as e:
            await message.reply_text("Ошибка при возврате звёзд.")
            logging.error(f"Ошибка refund: {e}")
    else:
        await message.reply_text("Нет транзакций для возврата.")
        logging.info(f"Команда /refund: нет транзакций для пользователя {user_id}")

# Обработчик callback-запросов (выбор количества звёзд)
@app.on_callback_query()
async def handle_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data.startswith("stars_"):
        amount = int(data.split("_")[1])
        user_payment_state[user_id]["amount"] = amount
        # Создаём инвойс для оплаты Telegram Stars
        try:
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
            logging.info(f"Чек на {amount} звёзд создан для пользователя {user_id}")
        except Exception as e:
            await callback_query.message.edit_text("Ошибка при создании чека.")
            logging.error(f"Ошибка при создании инвойса: {e}")
    elif data == "cancel":
        if user_id in user_payment_state:
            del user_payment_state[user_id]
            await callback_query.message.edit_text("Действие отменено.")
            logging.info(f"Callback cancel выполнен для пользователя {user_id}")
        else:
            await callback_query.message.edit_text("Нет активных действий для отмены.")
            logging.info(f"Callback cancel: нет активных действий для пользователя {user_id}")

class Application:
    @staticmethod
    async def run() -> None:
        set_window_title(get_app_info())
        display_title(get_app_info(), LANGUAGE)
        async with app:
            try:
                me = await app.get_me()
                logging.info(f"Авторизован как {me.username}")
                await send_start_message(app)
                await gift_monitoring(app, process_gift)
                await idle()  # Держит бота активным 24/7
            except Exception as e:
                logging.error(f"Ошибка при выполнении: {e}")
                raise

    @staticmethod
    def main() -> None:
        try:
            asyncio.run(Application.run())
        except KeyboardInterrupt:
            logging.info("Программа завершена пользователем")
        except Exception as e:
            logging.error(f"Непредвиденная ошибка: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    Application.main()
