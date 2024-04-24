import asyncio
import discord
from discord import app_commands
import sys

MY_GUILD = discord.Object(id=469406837608022027)  # replace with your guild id
MY_GUILD_2 = discord.Object(id=1232564395964633150)  # replace with your guild id (this one is optional)

with open('.env', 'r') as file:
    content = file.read().strip()

    if 'BOT_TOKEN = "' in content and 'OWNER_ID = "' in content:
        lines = content.split('\n')
        token = None
        owner_uid = None

        for line in lines:
            line = line.strip()

            if line.startswith('BOT_TOKEN = "') and line.endswith('"'):
                token = line.split('"')[1]
            elif line.startswith('OWNER_ID = "') and line.endswith('"'):
                owner_uid = line.split('"')[1]

        if token and owner_uid:
            if owner_uid.isdigit():
                owner_uid = int(owner_uid)
            else:
                print("Invalid owner ID format in '.env'. It should be a numeric value.")
                sys.exit(1)
        else:
            print("Missing or invalid BOT_TOKEN/OWNER_ID in '.env'. Refer to README.md for correct format.")
            sys.exit(1)
    else:
        print("Invalid format in '.env'. Refer to README.md for correct format.")
        sys.exit(1)


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        self.tree.copy_global_to(guild=MY_GUILD_2)
        await self.tree.sync(guild=MY_GUILD_2)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("-------------------------------")


@client.tree.command(name="test_bot_is_running", description="Replies with hello!")
async def running_test(interaction: discord.Interaction):
    # noinspection PyUnresolvedReferences
    await interaction.response.send_message(f"Hello, {interaction.user.mention}", ephemeral=True)


@client.tree.command(name="shutdown", description="Shuts down the bot")
async def shutdown_bot(interaction: discord.Interaction):
    # Replace 'YOUR_USER_ID' with your actual Discord user ID
    if interaction.user.id == owner_uid:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message("Shutting down the bot...")
        await client.close()
    else:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message("You don't have permission to shut down the bot.", ephemeral=True)


@client.tree.command(name="send_message", description="Sends the text into the current channel.")
@app_commands.rename(text_to_send="text")
@app_commands.describe(text_to_send="Text to send in the current channel")
async def send(interaction: discord.Interaction, text_to_send: str):
    if "@everyone" in text_to_send:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message("Nice try 😉", ephemeral=True)
    elif "@here" in text_to_send:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message("Nice try 😉", ephemeral=True)
    else:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message(text_to_send)


@client.tree.command(name="delete_messages", description="Deletes defined number of messages from the current channel.")
@app_commands.rename(to_delete="how_many_messages")
@app_commands.describe(to_delete="Number of messages to delete")
async def send(interaction: discord.Interaction, to_delete: int):
    # noinspection PyUnresolvedReferences
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.followup.send("Invalid permissions")
        return
    if to_delete <= 0:
        await interaction.followup.send("Invalid number")
        return
    else:
        # noinspection PyUnresolvedReferences
        await interaction.followup.send("Deleting...")
        await interaction.channel.purge(limit=to_delete)
        await interaction.edit_original_response(content=f"Deleted {to_delete} messages.")


@client.tree.command(name="add_numbers", description="Adds two numbers together")
@app_commands.describe(first_value="The first value you want to add something to",
                       second_value="The value you want to add to the first value")
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    try:
        # noinspection PyUnresolvedReferences
        await interaction.response.defer(ephemeral=True, thinking=False)
        # noinspection PyUnresolvedReferences
        await interaction.followup.send(f"{first_value} + {second_value} = {first_value + second_value}")
    except Exception as e:
        await asyncio.sleep(2)
        # noinspection PyUnresolvedReferences
        print(f"An error occurred: {str(e)}")
        await interaction.followup.send("An error occurred while processing the command.")


@client.tree.command(name="ping", description="Get bot latency")
async def ping(interaction: discord.Interaction):
    try:
        # noinspection PyUnresolvedReferences
        await interaction.response.defer(ephemeral=True)  # Defer the response

        # Get the bot's latency
        latency = round(client.latency * 1000)

        # Send the ping as a followup message
        await interaction.followup.send(f"Pong! Latency: {latency}ms")
    except Exception as e:
        # Handle any exceptions
        print(f"An error occurred: {str(e)}")
        await interaction.followup.send("An error occurred while processing the command.")


client.run(token)
