<h2 align="center">
  Telegram Gifts Auto-Buyer<br/>
</h2>

This user-bot automates the process of sending gifts to users on Telegram. The bot sends star gifts to specific users and can be configured to handle both limited and non-limited gifts. It also manages a set of configurations that control the bot's behavior, such as gift price limits, sender anonymity, and more.

## Table of Contents
- [General Configuration](#general-configuration)
- [Settings](#settings)
- [File and Data Paths](#file-and-data-paths)
- [Gifts & User Info](#gifts--user-info)
- [Custom Settings](#custom-settings)
- [How to Use](#how-to-use)

## General Configuration

### `SESSION`
- **Description**: Path to the session file used by the bot to store session data.
- **Default**: `"data/account"`

### `API_ID` & `API_HASH`
- **Description**: Your Telegram API ID & HASH. You need to create an application on [Telegram's website](https://my.telegram.org/auth) to get this ID & HASH.


## Settings

### `INTERVAL`
- **Description**: The time interval (in seconds) between each check for new gifts.
- **Default**: `5`

### `TIMEZONE`
- **Description**: The timezone in which the bot operates. This is used for time-based operations like logging.
- **Default**: `"Europe/Moscow"`

### `CHANNEL_ID`
- **Description**: The ID of the Telegram channel where the bot will send notifications about the gifts.

## File and Data Paths

### `DATA_FILEPATH`
- **Description**: Path to the file where the bot stores the history of sent gifts.
- **Default**: `"data/history.json"`

## Gifts & User Info

### `USER_ID`
- **Description**: List of user IDs that the bot will send gifts to. Users must have mutual contacts with the bot (i.e., both the bot and the user must be in the same group or channel).

### `MAX_GIFT_PRICE`
- **Description**: The maximum allowed price for a gift. The bot will only send gifts below this price.
- **Default**: `100`

### `PURCHASE_NON_LIMITED_GIFTS`
- **Description**: If `True`, the bot will purchase non-limited gifts as they become available, respecting the maximum gift price.
- **Default**: `True`

### `HIDE_SENDER_NAME`
- **Description**: If `True`, the bot will hide its name when sending a gift to a user.
- **Default**: `True`

### `GIFT_IDS`
- **Description**: A list of specific gift IDs that the bot will send. This is optional, and if not specified, all available gifts may be sent.

## Custom Settings

### Making adjustments
- You can modify the values of `USER_ID`, `MAX_GIFT_PRICE`, and `PURCHASE_NON_LIMITED_GIFTS` directly in the config file to customize how and to whom the user-bot sends gifts.
- Set the `PURCHASE_NON_LIMITED_GIFTS` to `False` if you do not want the bot to automatically buy non-limited gifts.

## How to Use

1. Clone or download the repository.
2. Ensure you have Python 3.10+ installed.
3. Install dependencies by running:

    ```bash
    pip install -r requirements.txt
    ```

4. Edit the `config.py` file to include your API credentials, user IDs, gift IDs, and other relevant settings.
5. Run the bot:

    ```bash
    python main.py
    ```

The bot will start sending gifts according to the configuration. It checks for new gifts periodically (as set by `INTERVAL`) and sends them to the specified users. Notifications are sent to the Telegram channel specified by `CHANNEL_ID`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
