# Requirements

This project requires discord.py version 2.3.2 which can be installed via `requirements.txt`:

```bash
pip install -r requirements.txt
```

# How to input your bot token and UID

1. Create an ``.env`` file in the bot's root folder.
2. Format the ``.env`` file as follows, replacing ``TOKEN_HERE``, ``OWNER_UID_HERE`` and ``VIRUS_TOTAL_API_KEY_HERE`` with your bot's token, your Discord UID and VirusTotal API key respectively. Keep the double quotation marks.
```text
BOT_TOKEN = "TOKEN_HERE"
OWNER_ID = "OWNER_UID_HERE"
VT_ID = "VIRUS_TOTAL_API_KEY_HERE"
```
For example:
```text
BOT_TOKEN = "12ab56c89"
OWNER_ID = "123456789"
VT_ID = "12ab56c89"
```
Owner_ID must be a numeric value

3. The ``.gitignore`` file will ignore the ``.env``.<br>

### Note:

If you want to change the location of the .env file, you will need to update the reference for it in main.py line 9.
```python
with open('path/to/.env', 'r') as file:
    content = file.read().strip()
```

# How to run

Open a command line in the same folder as the main.py script (Make sure python is installed and/or your python venv is active) and type:
```bash
python main.py
```

# Getting your Discord UID
If you don't know how to get your Discord UID, [click here](https://support.playhive.com/discord-user-id/).
