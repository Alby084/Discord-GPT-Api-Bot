# Requirements

This project requires discord.py version 2.3.2 and OpenAI version 1.30.1 which can be installed via `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Manually install requirements:

```bash
pip install discord.py~=2.3.2
```

```bash
pip install openai~=1.30.1
```

# How to input your bot token and UID

1. Create an ``.env`` file in the bot's root folder. (Same folder as main.py)
2. Format the ``.env`` file as follows, replacing ``TOKEN_HERE``, ``OWNER_UID_HERE`` and ``CHAT_GPT_API_KEY_HERE`` with your bot's token, your Discord UID and ChatGPT API key respectively. Keep the double quotation marks.
```text
BOT_TOKEN = "TOKEN_HERE"
OWNER_ID = "OWNER_UID_HERE"
GPT_API_KEY = "CHAT_GPT_API_KEY_HERE"
```
For example:
```text
BOT_TOKEN = "12ab56c89"
OWNER_ID = "123456789"
GPT_API_KEY = "12ab56c89"
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
1. On Discord, go to Settings > Advanced
2. Scroll down and make sure that Developer Mode is **on**
3. Exit settings and left click on your profile picture at the bottom left of discord (same place as the settings button) and click "Copy User ID" as shown below:

<img src="https://github.com/Alby084/Discord-GPT-Api-Bot/assets/99786431/a6de8ccb-206b-4656-abe2-35bb36751f7f" alt="drawing" width="380"/>
