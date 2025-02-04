## 1. Create a Telegram Bot:
Open Telegram and search for @BotFather
Start a chat with @BotFather
Type the command:
```bash
/newbot
```
## Follow the prompts:
Choose a name for your bot (e.g., MyTaskBot).
Choose a username (must end with bot, e.g., MyTaskBot123).
Copy the provided bot token (you’ll need it later). The format will be:
```bash
1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890
```
## 2. Get Your Chat ID:
# For Personal Chats:
Search for @userinfobot in Telegram and start the bot.
It will automatically send you your Chat ID.
# For Group Chats:
Add your bot to the group.
Send any message in the group.
Open this URL in a browser (replace <BOT_TOKEN> with your actual bot token):
```bash
https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```
Look for the "chat": {"id": ...} entry in the response.
For example:
```bash
"chat": {"id": -1001234567890, "type": "supergroup"}
```
Your Group Chat ID is -1001234567890.

# 3. Example Code to Send Messages to Telegram:
Once you have your BOT_TOKEN and CHAT_ID, you can use the following code to send messages.

```bash
import requests

BOT_TOKEN = "your_bot_token"  # Replace with your Telegram bot token
CHAT_ID = "your_chat_id"  # Replace with your chat ID

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    response = requests.get(url, params=params)
    return response.json()

# Example usage
message = "Hello, this is a message from your bot!"
send_telegram_message(message)
```

# 4. Set Up Your Environment:
Make sure you have Python installed.
Install requests to send HTTP requests:
```bash
pip install requests
```
