# Requirements

This project requires discord.py version 2.3.2 and OpenAI version 1.30.1 which can be installed via `requirements.txt`:

```bash
pip install -r requirements.txt
```

#### Manually install requirements:

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

<img src="https://cdn.discordapp.com/attachments/843759472613654550/1240133218536128532/image.png?ex=6645738f&is=6644220f&hm=9ae9446f1793025791cad87a0aad650131a1b8f932b096da4e33f98908dc1f3e&" alt="drawing" width="380"/>
