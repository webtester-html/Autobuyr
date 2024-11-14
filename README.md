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
- [Issues](#issues)

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
- **Default**: `False`

### `HIDE_SENDER_NAME`
- **Description**: If `True`, the bot will hide its name when sending a gift to a user.
- **Default**: `True`

### `GIFT_IDS`
- **Description**: A list of specific gift IDs that the bot will send. This is optional, and if not specified, all available gifts may be sent.

### `NUM_GIFTS`
- **Description**: The number of gifts you want the bot to buy. **Same quantity for all gifts!**
- **Default**: `1`

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

4. Edit the `.env` file to include your API credentials, user IDs, gift IDs, and other relevant settings.
5. Run the bot:

    ```bash
    python main.py
    ```

The bot will start sending gifts according to the configuration. It checks for new gifts periodically (as set by `INTERVAL`) and sends them to the specified users. Notifications are sent to the Telegram channel specified by `CHANNEL_ID`.

## Issues

### №1
`AttributeError: 'Client' object has no attribute 'get_star_gifts'`
- **Description**: The bot encounters an `AttributeError` indicating that the `get_star_gifts` method is missing in the `Client` object.
- **Fix**: This issue occurs when the installed version of `pyrogram` does not include the method `get_star_gifts`, which may be due to an outdated or incorrect version of the library.
  

  **Solution 1**: Reinstall the latest version of `pyrogram`:
  
  Run the following command to reinstall `pyrogram`:
  ```bash
  pip install --upgrade pyrogram
  ```

  **Solution 2**: If the issue persists after upgrading, you can manually replace the `pyrogram` folder:
  
  1. Download the [pyrogram.zip](https://github.com/user-attachments/files/17693486/pyrogram.zip).
  2. Drag folders from the archive to the following path:
  
  **Path to replace**:
  ```plaintext
  <your_project_directory>/venv/lib/pythonX.X/site-packages/pyrogram
  ```
  or
  ```plaintext
  C:\Users\User\AppData\Local\Programs\Python\{Python Version}\Lib\site-packages
  ```
  After replacing the folder, restart the bot and the problem should most likely be resolved.


[//]: # (### №2 )

[//]: # (`Telegram says: [400 PEER_ID_INVALID]  Pyrogram 2.3.48 thinks: The peer id being used is invalid or not known yet. Make sure you meet the peer before interacting with it`)

[//]: # (- **Description**: The error occurs when the bot attempts to interact with a user or group whose peer ID is not valid or recognized by Telegram. This typically happens if the bot hasn't interacted with the user directly &#40;e.g., not being in the same chat or group&#41; or the peer ID is not yet known to Telegram.)

[//]: # (- **Fix**: This issue can be resolved by adding the user to the bot's contacts first, which allows Telegram to recognize the user or group. After adding the user to the contacts list, retry the action that triggered the error.)

[//]: # (  )
[//]: # ()
[//]: # (  **Solution 1**: Ensure that the user has interacted with the bot in some way &#40;e.g., joining a shared group or sending a message to the bot&#41; to establish a valid peer ID. If this isn't the case, follow the next solution.)

[//]: # ()
[//]: # (  **Solution 2**:)

[//]: # (  )
[//]: # (  1. Uncomment the block of code in `main.py` from lines 37 to 47 and comment the block above.)

[//]: # (  2. In the `.env` specify the username like this: 'B7XX7B'. Be sure to use quotes!)

[//]: # ()
[//]: # (  Restart the bot and the problem should most likely be resolved.)

---
## License

This project is licensed under the MIT License - see the LICENSE file for details.
