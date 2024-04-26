# Requirements

This project requires discord.py version 2.3.2 which can be installed via `requirements.txt`:

```bash
pip install -r requirements.txt
```

# How to input your bot token and UID

1. Create an ``.env`` file in the bot's root folder.
2. Format the ``.env`` file as follows, replacing ``TOKEN_HERE`` and ``OWNER_UID_HERE`` with your bot's token and your Discord UID respectively. Keep the double quotation marks.
```text
BOT_TOKEN = "TOKEN_HERE"
OWNER_ID = "OWNER_UID_HERE"
```
For example:
```text
BOT_TOKEN = "123456789"
OWNER_ID = "123456789"
```
3. The ``.gitignore`` file will ignore the ``.env``.<br>

### Note:

If you want to change the location of the .env file, you will need to update the reference for it in main.py line 9.
```python
with open('path/to/.env', 'r') as file:
    content = file.read().strip()
```

# Getting your Discord UID
If you don't know how to get your Discord UID, [click here](https://support.playhive.com/discord-user-id/).
