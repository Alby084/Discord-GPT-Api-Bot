# Requirements

This project requires discord.py version 2.3.2, OpenAI version 1.30.1 and python-dotenv version 1.0.1 which can be installed via `requirements.txt`:

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

```bash
pip install python-dotenv~=1.0.1
```

# ``.env`` File settup

1. Create a ``.env`` file in the bot's root folder. (Same folder as main.py)
2. Format the ``.env`` file as follows, replacing ``TOKEN_HERE``, ``OWNER_UID_HERE``, ``CHAT_GPT_API_KEY_HERE``, ``DISCORD_SERVER_1`` and ``DISCORD_SERVER_2`` with your bot's token, your Discord UID, ChatGPT API key and discord server ID's respectively. Keeping the double quotation marks.
```text
BOT_TOKEN = "TOKEN_HERE"
OWNER_ID = "OWNER_UID_HERE"
GPT_API_KEY = "CHAT_GPT_API_KEY_HERE"
DISCORD_SERVER_1 = "FIRST_DISCORD_SERVER_ID_HERE"
DISCORD_SERVER_2 = "SECOND_DISCORD_SERVER_ID_HERE"
```
For example:
```text
BOT_TOKEN = "12ab56c89"
OWNER_ID = "123456789"
GPT_API_KEY = "12ab56c89"
DISCORD_SERVER_1 = "123456789"
DISCORD_SERVER_2 = "123456789"
```
``OWNER_ID``, ``DISCORD_SERVER_1`` and ``DISCORD_SERVER_2``  must be a numeric whole value

3. The ``.gitignore`` file will ignore the ``.env``.<br>

### Note:

If you want to change the location of the ``.env`` file, you will need to make a reference for it by adding:
```python
dotenv_path = os.path.join("path/to/env", ".env")
```

above ``load_dotenv(override=True)`` and update ``load_dotenv(override=True)`` to:
```python
load_dotenv(dotenv_path, override=True)
```

If you want to change your ``.env`` file name as well add this reference to the ``.env``:
```python
dotenv_path = os.path.join("path/to/env", "Env_Name_Here.env")
```

# How to run

Open a new command line in the same folder as the main.py script (Make sure python is installed and/or your python venv is active) and type:
```bash
python main.py
```

# Getting ID's and tokens

### Getting your discord UID
1. On Discord, go to Settings > Advanced
2. Scroll down and make sure that Developer Mode is **on**
3. Exit settings and left click on your profile picture at the bottom left of discord (same place as the settings button) and click ``Copy User ID`` as shown below:

<img src="https://github.com/Alby084/Discord-GPT-Api-Bot/assets/99786431/a6de8ccb-206b-4656-abe2-35bb36751f7f" alt="drawing" width="380"/> <br>

### Getting discord server ID
1. On Discord, go to Settings > Advanced
2. Scroll down and make sure that Developer Mode is **on**
3. Exit settings and right click on the server(s) your bot is in
and click ``Copy Server ID`` as shown below:

<img src="https://github.com/Alby084/python-beginner-projects/assets/99786431/cd4e8349-b916-4f51-adc4-fd774465483f" alt="drawing" width="220"/> <br>

### Getting chat GPT API key
1. Visit the openai playground website settings page [Here](https://platform.openai.com/settings/organization/general).
2. Click the ``Create Project`` button at the bottom of the settings list as shown below:
3. Name your project and click the ``Create`` button.
4. Navigate to the ``API keys`` page above the settings page on the left side navigation pannel. Alternatively you can click [Here](https://platform.openai.com/api-keys).
5. Click the ``Create new secret key`` button.
6. Choose ``You`` under ``Owned by``. Name your API key something descriptive and select the new project you just created in the ``Project`` dropdown. Set ``Permissions`` as ``All`` and click the ``Create secret key`` button as shown below:

### Note on GPT ``Credit balance``:
Ensure you have an available ``Credit balance``. You can check on the ``Billing`` page in ``Settings`` or by clicking [Here](https://platform.openai.com/settings/organization/billing/overview). If you do not have a ``Credit balance`` you will need to add money (credit) to your account otherwise this discord bot's chat GPT functionality will not work.