# Requirements
Requires discord.py version 2.3.2 which can be installed via requirements.txt
```
pip install -r requirements.txt
```

# How to input your bot token and UID

Create an ".env" file in the bots root folder and format the ".env" as follows.\
Replace "TOKEN_HERE" and "OWNER_UID_HERE" with your bots token and your discord UID respectively
but keep the double quotation marks. e.g. BOT_TOKEN = "123456789", OWNER_ID = "123456789".\
The .gitignore will ignore this file.

```
BOT_TOKEN = "TOKEN_HERE"
OWNER_ID = "OWNER_UID_HERE"
```

If you want to change the ".env" file location you will need to update the reference for it in main.py.\
Don't know how do get your discord UID? [click here](https://support.playhive.com/discord-user-id/).
