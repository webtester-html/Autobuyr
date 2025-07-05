import asyncio
import traceback
import configparser
import logging
from pyrogram import Client  # Используем pyrogram вместо pyrofork

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Чтение конфига
config = configparser.ConfigParser()
try:
    config.read('config.ini')
    logging.info("Файл config.ini успешно прочитан")
except Exception as e:
    logging.error(f"Ошибка чтения config.ini: {e}")
    raise

# Параметры из конфига
try:
    API_ID = int(config['Telegram']['API_ID'])  # 24122577
    API_HASH = config['Telegram']['API_HASH']   # 428513682803fb9f74a7754aafdd38ce
    PHONE_NUMBER = config['Telegram']['PHONE_NUMBER']  # +380680929672
    CHANNEL_ID = config['Telegram']['CHANNEL_ID']  # -100
    INTERVAL = int(config['Bot']['INTERVAL'])  # 10
    LANGUAGE = config['Bot']['LANGUAGE']  # RU
    HIDE_SENDER_NAME = config['Bot']['HIDE_SENDER_NAME'].lower() == 'true'  # True
    GIFT_RANGES = config['Gifts']['GIFT_RANGES']  # 1-1000: 500000 x 5: @sacoectasy, 6956377285;
    PURCHASE_ONLY_UPGRADABLE_GIFTS = config['Gifts']['PURCHASE_ONLY_UPGRADABLE_GIFTS'].lower() == 'true'  # False
    PRIORITIZE_LOW_SUPPLY = config['Gifts']['PRIORITIZE_LOW_SUPPLY'].lower() == 'true'  # True
    SESSION = config['Telegram']['SESSION']  # gifts_session
    logging.info("Все параметры из config.ini успешно загружены")
except Exception as e:
    logging.error(f"Ошибка при чтении параметров из config.ini: {e}")
    raise

# Заглушка для отсутствующих модулей
def display_title(app_info, language): logging.info(f"Заглушка: display_title({app_info}, {language})")
def get_app_info(): return {"name": "GiftBot", "version": "1.0"}
def set_window_title(app_info): logging.info(f"Заглушка: set_window_title({app_info})")
async def send_start_message(client): 
    await client.send_message("me", "Бот запущен на Render!")
    logging.info("Тестовое сообщение отправлено в 'Saved Messages'")
async def gift_monitoring(client, callback): 
    logging.info("Заглушка: gift_monitoring запущен")
async def process_gift(client, gift): 
    logging.info(f"Заглушка: process_gift({gift})")

class Application:
    @staticmethod
    async def run() -> None:
        set_window_title(get_app_info())
        display_title(get_app_info(), LANGUAGE)

        async with Client(
                name=SESSION,  # gifts_session
                api_id=API_ID,
                api_hash=API_HASH,
                phone_number=PHONE_NUMBER
        ) as client:
            try:
                me = await client.get_me()
                logging.info(f"Авторизован как {me.first_name} (@{me.username})")
                await send_start_message(client)
                await gift_monitoring(client, process_gift)
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
