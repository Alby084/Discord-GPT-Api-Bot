import discord
from discord.ext import commands
import sys


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    # This example requires the 'message_content' intent.
    async def on_message(self, message):
        print(f'Message from {message.author} in {message.guild}: {message.content}')
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!hello'):
            await message.reply('Hello!', mention_author=True)


intents = discord.Intents.default()
intents.message_content = True

with open('.env', 'r') as file:
    content = file.read().strip()
    if content.startswith('BOT_TOKEN = "') and content.endswith('"'):
        token = content.split('"')[1]
        print(token)
    else:
        print("Invalid token format in '.env' Refer to the README.md on how to format the '.env' file")
        sys.exit(1)

client = MyClient(intents=intents)
client.run(token)
