import discord
import functools
from discord import app_commands, ui # Import ui for Views
import sys
import os
from dotenv import load_dotenv
from Chat_GPT_Function import gpt, deepseek, dalle3, dalle2
import json
from datetime import datetime, timedelta
import time
import asyncio
import logging
import math # Import math for ceiling division

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(override=True)

# --- Environment Variable Loading and Validation ---
error_messages = [] # Stores critical errors that prevent startup
warnings = [] # Stores warnings about missing optional features

token = os.getenv("BOT_TOKEN")
owner_id_str = os.getenv("OWNER_ID")
gpt_key = os.getenv("GPT_API_KEY")
openrouter_deepseek_key = os.getenv("OPENROUTER_DEEPSEEK_API_KEY") # Load the Deepseek key
discord_server_1_str = os.getenv("DISCORD_SERVER_1")
discord_server_2_str = os.getenv("DISCORD_SERVER_2") # Optional

owner_uid = None
discord_server_1_id = None
discord_server_2_id = None # Initialize optional server ID as None

# Validate BOT_TOKEN (Required)
if not token:
    error_messages.append("CRITICAL: BOT_TOKEN environment variable is not set.")

# Validate OWNER_ID (Required)
if owner_id_str:
    try:
        owner_uid = int(owner_id_str)
    except ValueError:
        error_messages.append("CRITICAL: OWNER_ID environment variable must be a valid integer.")
else:
    error_messages.append("CRITICAL: OWNER_ID environment variable is not set.")

# Validate GPT_API_KEY (Treating as Required for core functionality)
if not gpt_key:
    error_messages.append("CRITICAL: GPT_API_KEY environment variable is not set.")

# Validate OPENROUTER_DEEPSEEK_API_KEY (Optional - Log Warning if missing)
if not openrouter_deepseek_key:
    error_messages.append("CRITICAL: OPENROUTER_DEEPSEEK_API_KEY is not set.")
# else:
#     # Optional: Log confirmation that the key was found
#     logger.info("OPENROUTER_DEEPSEEK_API_KEY found.")


# Validate DISCORD_SERVER_1 (Required)
if discord_server_1_str:
    try:
        discord_server_1_id = int(discord_server_1_str)
    except ValueError:
        error_messages.append("CRITICAL: DISCORD_SERVER_1 environment variable must be a valid integer.")
else:
    error_messages.append("CRITICAL: DISCORD_SERVER_1 environment variable is not set.")

# Validate DISCORD_SERVER_2 (Optional)
if discord_server_2_str:
    try:
        discord_server_2_id = int(discord_server_2_str)
        logger.info(f"Optional Discord Server 2 ID loaded: {discord_server_2_id}")
    except ValueError:
        # Log warning but don't prevent startup
        warnings.append(f"Warning: DISCORD_SERVER_2 is set ('{discord_server_2_str}') but is not a valid integer. Ignoring.")
        # Keep discord_server_2_id as None
else:
    logger.info("Optional Discord Server 2 ID (DISCORD_SERVER_2) not set.")

# Log any warnings found
if warnings:
    logger.warning("Configuration warnings:")
    for msg in warnings:
        logger.warning(f"- {msg}")

# Exit if any CRITICAL variables are missing or invalid
if error_messages:
    logger.critical("Critical configuration errors found:")
    for msg in error_messages:
        logger.critical(f"- {msg}")
    sys.exit("Exiting due to critical missing or invalid environment variables.")
else:
    logger.info("Required environment variables loaded successfully.")

# --- End Environment Variable Loading ---

# Create discord.Object instances only for valid server IDs
discord_server_1 = discord.Object(id=discord_server_1_id)
discord_server_2 = discord.Object(id=discord_server_2_id) if discord_server_2_id else None # Create Object only if ID is valid

# Load GPT Parameters from JSON
try:
    with open("GPT_Parameters.json") as f:
        data = json.load(f)  # Loads the gpt system prompts
    # Ensure 'character_limit_prompt' exists, provide default if not
    char_limit = data.get("system_content", [{}])[0].get("character_limit_prompt", " Your response must not exceed 4096 characters")
except FileNotFoundError:
    logger.error("Error: GPT_Parameters.json not found.")
    sys.exit("Exiting due to missing configuration file.")
except (KeyError, IndexError, json.JSONDecodeError) as e:
    logger.error(f"Error reading GPT_Parameters.json: {e}")
    sys.exit("Exiting due to invalid configuration file format.")


# --- Help Command Pagination View ---
class HelpView(ui.View):
    def __init__(self, *, commands: list, items_per_page: int, interaction: discord.Interaction):
        super().__init__(timeout=180.0)  # View times out after 180 seconds
        self.commands = commands
        self.items_per_page = items_per_page
        self.total_pages = math.ceil(len(self.commands) / self.items_per_page)
        self.current_page = 1
        self.interaction = interaction # Store the original interaction
        self.update_buttons() # Initial button state

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only allow the original user to interact with the buttons
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("You cannot control this help menu.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        # Disable buttons on timeout
        for item in self.children:
            if isinstance(item, ui.Button):
                item.disabled = True
        try:
            # Edit the original message to show disabled buttons
            await self.interaction.edit_original_response(view=self)
        except discord.NotFound:
            logger.warning("Original help message not found for timeout update.")
        except discord.HTTPException as e:
             logger.error(f"Failed to edit help message on timeout: {e}")

    def get_page_embed(self) -> discord.Embed:
        """Generates the embed for the current page."""
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        page_commands = self.commands[start_index:end_index]

        embed = discord.Embed(
            title=f"Help - Page {self.current_page}/{self.total_pages}",
            description="Here are the available commands:",
            color=discord.Color.blue(),
        )
        # Use bot's avatar URL safely
        avatar_url = self.interaction.client.user.avatar.url if self.interaction.client.user.avatar else None
        embed.set_author(
            name=self.interaction.client.user.name,
            icon_url=avatar_url,
        )

        if not page_commands:
            embed.description = "No commands found on this page."
        else:
            for command in page_commands:
                # --- Potential Problem Area ---
                field_name = f"/{command.name}"
                # The current code handles `None` description, but maybe not an empty string ""?
                field_value = command.description or 'No description available.'

                # Add checks to ensure name and value are not empty before adding
                if not field_name or not field_value:
                     logger.warning(f"Skipping command '{command.name}' in help embed due to empty name/value. Name: '{field_name}', Value: '{field_value}'")
                     continue # Skip adding this field if either part is empty

                # Also check lengths (optional but good practice)
                if len(field_name) > 256:
                    logger.warning(f"Command name '/{command.name}' exceeds 256 chars, truncating for help.")
                    field_name = field_name[:253] + "..." # Truncate safely
                if len(field_value) > 1024:
                    logger.warning(f"Command description for '/{command.name}' exceeds 1024 chars, truncating for help.")
                    field_value = field_value[:1021] + "..." # Truncate safely

                embed.add_field(
                    name=field_name,
                    value=field_value,
                    inline=False,
                )

        embed.set_footer(text=f"Showing commands {start_index + 1}-{min(end_index, len(self.commands))} of {len(self.commands)}")
        return embed

    def update_buttons(self):
        """Enable/disable buttons based on the current page."""
        # Find buttons by custom_id (more reliable than order)
        prev_button = discord.utils.get(self.children, custom_id="prev_page")
        next_button = discord.utils.get(self.children, custom_id="next_page")

        if prev_button:
            prev_button.disabled = self.current_page == 1
        if next_button:
            next_button.disabled = self.current_page == self.total_pages

    @ui.button(label="Previous", style=discord.ButtonStyle.blurple, custom_id="prev_page", emoji="⬅️")
    async def previous_page(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()
            embed = self.get_page_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
             # Should be disabled, but handle defensively
             await interaction.response.defer()


    @ui.button(label="Next", style=discord.ButtonStyle.blurple, custom_id="next_page", emoji="➡️")
    async def next_page(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_buttons()
            embed = self.get_page_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            # Should be disabled, but handle defensively
            await interaction.response.defer()

# --- End Help Command Pagination View ---


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # Optional: Uncomment and adjust setup_hook if you want auto-syncing on startup
    # async def setup_hook(self):
    #     logger.info(f"Copying global commands to guild {discord_server_1.id}...")
    #     self.tree.copy_global_to(guild=discord_server_1)
    #     await self.tree.sync(guild=discord_server_1)
    #     logger.info(f"Synced commands to guild {discord_server_1.id}.")
    #
    #     if discord_server_2: # Only sync to server 2 if it's configured
    #         logger.info(f"Copying global commands to guild {discord_server_2.id}...")
    #         self.tree.copy_global_to(guild=discord_server_2)
    #         await self.tree.sync(guild=discord_server_2)
    #         logger.info(f"Synced commands to guild {discord_server_2.id}.")
    #     logger.info("Command sync process completed in setup_hook.")


intents = discord.Intents.default()
# Required for clear command potentially, depending on exact discord.py version and usage
# intents.messages = True # Uncomment if needed for message content or certain purge operations
intents.message_content = False # Explicitly disable if not needed

client = MyClient(intents=intents)


@client.event
async def on_ready():
    logger.info(f"---------------------------------------------")
    logger.info(f"Logged in as {client.user} (ID: {client.user.id})")
    logger.info(f"discord.py version: {discord.__version__}")
    logger.info(f"Owner ID: {owner_uid}")
    logger.info(f"Primary Guild ID: {discord_server_1.id}")
    if discord_server_2:
        logger.info(f"Secondary Guild ID: {discord_server_2.id}")
    else:
        logger.info(f"Secondary Guild ID: Not configured")
    logger.info(f"---------------------------------------------")

    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="For Slash Commands"
        )
    )

    # Optional: DM owner on startup
    # try:
    #     dm_user = await client.fetch_user(owner_uid)
    #     await dm_user.send("Bot Online!")
    #     logger.info(f"Sent online notification DM to owner (ID: {owner_uid}).")
    # except discord.NotFound:
    #     logger.warning(f"Could not find owner user with ID {owner_uid} to send DM.")
    # except discord.Forbidden:
    #     logger.warning(f"Bot lacks permission to DM owner user (ID: {owner_uid}).")
    # except Exception as e:
    #     logger.error(f"Failed to send online notification DM: {e}")


@client.tree.command(name="sync", description="Syncs slash commands to the servers (Owner only)")
async def sync(interaction: discord.Interaction):
    if interaction.user.id != owner_uid:
        await interaction.response.send_message(
            "You don't have permission to sync commands.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True, thinking=True)
    logger.info(f"Sync command initiated by owner (ID: {interaction.user.id}).")

    try:
        synced_guilds = []
        # Clear and sync for server 1
        logger.info(f"Clearing commands for guild {discord_server_1.id}...")
        client.tree.clear_commands(guild=discord_server_1)
        await client.tree.sync(guild=discord_server_1)
        logger.info(f"Copying global commands to guild {discord_server_1.id}...")
        client.tree.copy_global_to(guild=discord_server_1)
        await client.tree.sync(guild=discord_server_1)
        synced_guilds.append(str(discord_server_1.id))
        logger.info(f"Successfully synced commands for guild {discord_server_1.id}.")

        # Clear and sync for server 2 if it exists
        if discord_server_2:
            logger.info(f"Clearing commands for guild {discord_server_2.id}...")
            client.tree.clear_commands(guild=discord_server_2)
            await client.tree.sync(guild=discord_server_2)
            logger.info(f"Copying global commands to guild {discord_server_2.id}...")
            client.tree.copy_global_to(guild=discord_server_2)
            await client.tree.sync(guild=discord_server_2)
            synced_guilds.append(str(discord_server_2.id))
            logger.info(f"Successfully synced commands for guild {discord_server_2.id}.")
        else:
             logger.info("Skipping sync for optional second server (not configured).")

        await interaction.followup.send(
            f"Successfully synced commands to guilds: {', '.join(synced_guilds)}",
            ephemeral=True
        )
    except discord.HTTPException as e:
        logger.error(f"HTTPException during sync: {e.status} {e.text}")
        await interaction.followup.send(
            f"An error occurred during sync (HTTP {e.status}). Check logs.",
            ephemeral=True
        )
    except Exception as e:
        logger.exception(f"An unexpected error occurred during sync:") # Logs traceback
        await interaction.followup.send(
            "An unexpected error occurred while syncing commands. Check logs.",
            ephemeral=True
        )


# -------------------------- HELP COMMAND (PAGINATED) ----------------------------------
@client.tree.command(name="help", description="Lists all available slash commands")
async def help_command(interaction: discord.Interaction):
    try:
        # Get all registered commands
        all_commands = client.tree.get_commands()

        # Filter out owner-only commands if the user is not the owner
        if interaction.user.id != owner_uid:
            commands_to_show = [cmd for cmd in all_commands if cmd.name not in ["sync", "shutdown"]]
        else:
            commands_to_show = all_commands # Owner sees all commands

        # Sort commands alphabetically by name
        commands_to_show.sort(key=lambda cmd: cmd.name)

        if not commands_to_show:
            await interaction.response.send_message("There are no commands available for you to use.", ephemeral=True)
            return

        # Define how many commands per page
        commands_per_page = 5 # Adjust as needed

        # Create the view instance, passing the filtered commands and interaction
        view = HelpView(commands=commands_to_show, items_per_page=commands_per_page, interaction=interaction)

        # Get the embed for the first page
        first_page_embed = view.get_page_embed()

        # Send the initial message with the first page and the view
        await interaction.response.send_message(embed=first_page_embed, view=view, ephemeral=False) # Make help visible

    except Exception as e:
        logger.exception("Error occurred in help command:")
        # Avoid sending again if already responded/deferred
        if not interaction.response.is_done():
            await interaction.response.send_message("An error occurred while fetching the command list.", ephemeral=True)
        else:
            await interaction.followup.send("An error occurred while fetching the command list.", ephemeral=True)


# -------------------------- TEST COMMAND ----------------------------------
@client.tree.command(name="test_bot", description="Replies with 'Hello!'")
async def running_test(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hello, {interaction.user.mention}!", ephemeral=True
    )


# -------------------------- SHUTDOWN ----------------------------------
@client.tree.command(
    name="shutdown", description="Shuts down the bot (Owner only)"
)
async def shutdown_bot(interaction: discord.Interaction):
    if interaction.user.id == owner_uid:
        logger.warning(f"Shutdown command received from owner (ID: {interaction.user.id}). Shutting down.")
        await interaction.response.send_message("Shutting down...", ephemeral=True)
        await client.close()
    else:
        logger.warning(f"Unauthorized shutdown attempt by user (ID: {interaction.user.id}).")
        await interaction.response.send_message(
            "You don't have permission to shut down the bot.", ephemeral=True
        )


# -------------------------- DELETE MESSAGES ----------------------------------
@client.tree.command(
    name="clear",
    description="Deletes a specified number of messages from the current channel.",
)
@app_commands.checks.has_permissions(manage_messages=True) # Use decorator for permissions
@app_commands.describe(amount="Number of messages to delete (1-100)")
async def clear_messages(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]): # Use Range for validation, renamed function
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        deleted = await interaction.channel.purge(limit=amount)
        timestamp = discord.utils.format_dt(datetime.now(), style='F') # Formatted timestamp
        await interaction.followup.send(
            f"Successfully deleted {len(deleted)} messages. ({timestamp})", ephemeral=True
        )
        logger.info(f"User {interaction.user} cleared {len(deleted)} messages in channel {interaction.channel.id}.")
    except discord.Forbidden:
        logger.warning(f"Bot lacks 'Manage Messages' permission in channel {interaction.channel.id} for clear command.")
        await interaction.followup.send("I don't have permission to delete messages in this channel.", ephemeral=True)
    except discord.HTTPException as e:
        logger.error(f"HTTPException during message purge: {e.status} {e.text}")
        await interaction.followup.send("An error occurred while trying to delete messages.", ephemeral=True)
    except Exception as e:
        logger.exception("Unexpected error during clear command:")
        await interaction.followup.send("An unexpected error occurred.", ephemeral=True)

# Error handler for the clear command specifically for permission issues
@clear_messages.error
async def clear_messages_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    else:
        logger.error(f"Unhandled error in clear_messages: {error}")
        # Avoid sending a generic error if response already sent/deferred
        if not interaction.response.is_done():
             await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
        else:
             await interaction.followup.send("An unexpected error occurred.", ephemeral=True)


# -------------------------- BOT LATENCY ----------------------------------
@client.tree.command(name="ping", description="Checks the bot's latency")
async def ping(interaction: discord.Interaction):
    try:
        start_time = time.monotonic()
        # Defer first to acknowledge the command quickly
        await interaction.response.defer(ephemeral=True, thinking=True)
        latency = round(client.latency * 1000)
        end_time = time.monotonic()
        # Calculate interaction latency (time from defer to now)
        interaction_latency = round((end_time - start_time) * 1000)

        await interaction.followup.send(
            f"Pong! \nWebsocket Latency: {latency}ms\nInteraction Latency: {interaction_latency}ms",
             ephemeral=True
        )
    except Exception as e:
        logger.exception("Error occurred in ping command:")
        # Avoid sending again if already responded/deferred
        if not interaction.response.is_done():
            await interaction.response.send_message("An error occurred while measuring latency.", ephemeral=True)
        else:
            await interaction.followup.send("An error occurred while measuring latency.", ephemeral=True)


# --- Helper Function for API Commands ---
async def handle_api_command(interaction: discord.Interaction, title: str, api_func, *args):
    """Handles common logic for API commands: defer, call API, format embed, send response, handle errors."""
    try:
        # Use thinking=True for potentially long API calls
        await interaction.response.defer(ephemeral=False, thinking=True)

        # Run the blocking API call in an executor
        loop = asyncio.get_event_loop()
        api_response = await loop.run_in_executor(None, api_func, *args)

        if not api_response:
             logger.warning(f"API call {api_func.__name__} returned empty response for prompt: {args[1] if len(args) > 1 else 'N/A'}")
             await interaction.followup.send("The API returned an empty response. Please try again.", ephemeral=True)
             return

        # Check response length against Discord limits (Embed description limit is 4096)
        if len(api_response) > 4096:
            logger.warning(f"API response exceeded 4096 characters for {title}. Truncating.")
            api_response = api_response[:4093] + "..." # Truncate safely

        embed = discord.Embed(
            title=title,
            description=api_response,
            color=discord.Color.blue(),
        )
        avatar_url = client.user.avatar.url if client.user.avatar else None
        embed.set_author(
            name=client.user.name,
            icon_url=avatar_url,
        )
        # Optionally add timestamp or footer
        embed.timestamp = datetime.now()

        await interaction.followup.send(embed=embed)

    except Exception as e:
        logger.exception(f"Error occurred in API command '{title}':")
        error_message_user = "An error occurred while processing your request."
        # Check for specific OpenAI content policy violation format if applicable
        # (Adjust this based on the actual error structure from the OpenAI library)
        if "content_policy_violation" in str(e):
             try:
                 # Attempt to extract a more specific message (this parsing is fragile)
                 details = str(e).split("message': '", 1)[1].split("',", 1)[0]
                 error_message_user = f"Content Policy Violation: {details}"
             except IndexError:
                 error_message_user = "Your request was flagged due to content policy."

        # Use followup.send since we deferred
        try:
            await interaction.followup.send(error_message_user, ephemeral=True)
        except discord.NotFound:
             logger.error("Interaction expired before error message could be sent.")
        except discord.HTTPException as http_err:
             logger.error(f"Failed to send error followup: {http_err}")


# -------------------------- CORRECT GRAMMAR ----------------------------------
@client.tree.command(
    name = "gpt_correct_grammar", description = "Corrects grammar of inputted text"
)
@app_commands.describe(text = "Text to grammar correct")
async def gpt_correct_grammar(interaction: discord.Interaction, text: str): # Renamed function
    # Safely get system prompt, provide default if missing
    sys_prompt_base = data.get("system_content", [{}])[0].get("correct_grammar", "Correct the grammar:")
    sys_prompt = sys_prompt_base + char_limit
    await handle_api_command(interaction, "Corrected Grammar", gpt, "gpt-3.5-turbo-16k", text, sys_prompt, 0)


# -------------------------- WEBSITE ----------------------------------
@client.tree.command(
    name="gpt_single_page_website",
    description="Generates HTML for a single-page website based on specifications",
)
@app_commands.describe(specifications = "Describe the website page you want")
async def gpt_single_page_website(interaction: discord.Interaction, specifications: str): # Renamed function
    sys_prompt_base = data.get("system_content", [{}])[0].get("single_page_website", "Create a single page website:")
    sys_prompt = sys_prompt_base + char_limit
    await handle_api_command(interaction, "Single Page Website Code", gpt, "gpt-3.5-turbo-16k", specifications, sys_prompt, 0.7)


# -------------------------- TEXT TO EMOJI ----------------------------------
@client.tree.command(name = "gpt_text_to_emoji", description = "Converts text to emojis")
@app_commands.describe(text = "Text to convert to emojis (max 230 chars)")
async def gpt_text_to_emoji(interaction: discord.Interaction, text: str): # Renamed function
    if len(text) > 230:
        await interaction.response.send_message(
            "Input text is too long (max 230 characters).", ephemeral=True
        )
        return

    sys_prompt = data.get("system_content", [{}])[0].get("text_to_emoji", "Convert to emojis:")
    await handle_api_command(interaction, f'Text to Emoji for "{text}"', gpt, "gpt-3.5-turbo-16k", text, sys_prompt, 0.7)


# -------------------------- TEXT TO BLOCK LETTERS ----------------------------------
@client.tree.command(
    name="gpt_text_to_block_letters", description="Converts text into block letter emojis"
)
@app_commands.describe(text = "Text to convert into block letters")
async def gpt_text_to_block_letters(interaction: discord.Interaction, text: str): # Renamed function
    sys_prompt = data.get("system_content", [{}])[0].get("text_to_block_letters", "Convert to block letters:")
    await handle_api_command(interaction, "Text to Block Letters", gpt, "gpt-3.5-turbo-16k", text, sys_prompt, 0.7)


# -------------------------- CODE DEBUG ----------------------------------
@client.tree.command(name = "gpt_debug_code", description="Debugs your code using GPT-4")
@app_commands.describe(code = "Code snippet to debug")
async def gpt_debug_code(interaction: discord.Interaction, code: str): # Renamed function
    sys_prompt_base = data.get("system_content", [{}])[0].get("code_debug", "Debug this code:")
    sys_prompt = sys_prompt_base + char_limit
    await handle_api_command(interaction, "Code Debug Analysis", gpt, "gpt-4", code, sys_prompt, 0)


# -------------------------- SHORT STORY ----------------------------------
@client.tree.command(
    name = "gpt_short_story", description = "Writes a short story about a topic using GPT-4"
)
@app_commands.describe(topic = "What should the story be about?")
async def gpt_short_story(interaction: discord.Interaction, topic: str): # Renamed function
    sys_prompt = data.get("system_content", [{}])[0].get("short_story", "Write a short story:")
    await handle_api_command(interaction, f'Short Story about "{topic}"', gpt, "gpt-4", topic, sys_prompt, 0.7)


# -------------------------- GENERAL QUESTION (GPT) ----------------------------------
# Define choices for the model parameter
ModelChoices = app_commands.Choice(name="GPT-3.5 (Faster, Cheaper)", value="gpt-3.5-turbo-16k")
ModelChoices4 = app_commands.Choice(name="GPT-4 (Smarter, Slower)", value="gpt-4")

@client.tree.command(name = "ask_gpt", description = "Ask a general question to GPT") # Renamed command
@app_commands.describe(prompt = "What do you want to ask? (max 230 chars)")
@app_commands.describe(model = "Choose the GPT model to use")
@app_commands.choices(model=[ModelChoices, ModelChoices4]) # Use choices
async def ask_gpt(interaction: discord.Interaction, prompt: str, model: app_commands.Choice[str]): # Renamed function, use Choice type hint
    if len(prompt) > 230:
        await interaction.response.send_message(
            "Your question is too long (max 230 characters).", ephemeral=True
        )
        return

    sys_prompt = data.get("system_content", [{}])[0].get("general_questions_gpt", "Answer the question:")
    title = f'GPT ({model.name}) response to "{prompt}"' # Use choice name in title
    await handle_api_command(interaction, title, gpt, model.value, prompt, sys_prompt, 0.7) # Use choice value for API call


# -------------------------- GENERAL QUESTION (DEEPSEEK) ----------------------------------
@client.tree.command(name = "ask_deepseek", description = "Ask a general question to Deepseek") # Renamed command
@app_commands.describe(prompt = "What do you want to ask? (max 230 chars)")
async def ask_deepseek(interaction: discord.Interaction, prompt: str): # Renamed function
    if len(prompt) > 230:
         await interaction.response.send_message(
            "Your question is too long (max 230 characters).", ephemeral=True
        )
         return

    sys_prompt = data.get("system_content", [{}])[0].get("general_questions_deepseek", "Answer the question:")
    title = f'Deepseek response to "{prompt}"'
    # Note: deepseek function in Chat_GPT_Function.txt needs prompt and sys_prompt args
    await handle_api_command(interaction, title, deepseek, prompt, sys_prompt)


# --- Helper Function for DALL-E Commands ---
async def handle_dalle_command(interaction: discord.Interaction, api_func, prompt: str, **kwargs):
    """Handles common logic for DALL-E commands."""
    try:
        await interaction.response.defer(ephemeral=False, thinking=True)

        # Get the current time + 1 hour for expiry display
        future_time = datetime.now() + timedelta(hours=1)
        expiry_timestamp = int(time.mktime(future_time.timetuple()))

        # Run the blocking API call in an executor
        loop = asyncio.get_event_loop()

        # Create a partial function that packages api_func with its arguments
        # The 'prompt' is passed as the first positional argument to api_func
        # The items in 'kwargs' (like size, quality, style) are passed as keyword arguments to api_func
        func_call = functools.partial(api_func, prompt, **kwargs)

        # Now, run the 'func_call' (which takes no arguments itself) in the executor
        image_url = await loop.run_in_executor(None, func_call)


        if not image_url:
             logger.warning(f"DALL-E call {api_func.__name__} returned empty URL for prompt: {prompt}")
             await interaction.followup.send("The image generation failed or returned no URL.", ephemeral=True)
             return

        # Create embed for better presentation
        embed = discord.Embed(
            title="Image Generation Result",
            description=f"**Prompt:** {discord.utils.escape_markdown(prompt)}\n\n[Image Link]({image_url}) (Link expires <t:{expiry_timestamp}:R>)", # Escape prompt
            color=discord.Color.purple() # Or another suitable color
        )
        embed.set_image(url=image_url)
        avatar_url = client.user.avatar.url if client.user.avatar else None
        embed.set_author(
            name=client.user.name,
            icon_url=avatar_url,
        )
        # Use __name__ which should be 'dalle3' or 'dalle2'
        model_name = api_func.__name__.replace('dalle', 'DALL·E ').capitalize()
        embed.set_footer(text=f"Generated with {model_name}") # Indicate model used
        embed.timestamp = datetime.now()

        await interaction.followup.send(embed=embed)

    except Exception as e:
        logger.exception(f"Error occurred in DALL-E command '{api_func.__name__}':")
        error_message_user = "An error occurred while generating the image."
        # Check for specific OpenAI content policy violation format
        if "content_policy_violation" in str(e):
             try:
                 details = str(e).split("message': '", 1)[1].split("',", 1)[0]
                 error_message_user = f"Content Policy Violation: {details}"
             except IndexError:
                 error_message_user = "Your prompt was flagged due to content policy."
        elif "Invalid size" in str(e): # Example for specific API errors
             error_message_user = "An invalid image size was provided for the selected DALL-E model."
        elif "Rate limit" in str(e): # Example for rate limits
             error_message_user = "Rate limit reached. Please try again later."

        try:
            await interaction.followup.send(error_message_user, ephemeral=True)
        except discord.NotFound:
             logger.error("Interaction expired before DALL-E error message could be sent.")
        except discord.HTTPException as http_err:
             logger.error(f"Failed to send DALL-E error followup: {http_err}")


# -------------------------- DALLE 3 ----------------------------------
# Define choices for DALL-E 3 parameters
Dalle3Size = app_commands.Choice
Dalle3Quality = app_commands.Choice
Dalle3Style = app_commands.Choice

@client.tree.command(name = "dalle_3", description="Generates an image with DALL-E 3")
@app_commands.describe(prompt = "Describe the image you want DALL-E 3 to create")
@app_commands.describe(size = "Image dimensions")
@app_commands.choices(size=[
    Dalle3Size(name="Square (1024x1024)", value="1024x1024"),
    Dalle3Size(name="Wide (1792x1024)", value="1792x1024"),
    Dalle3Size(name="Tall (1024x1792)", value="1024x1792")
])
@app_commands.describe(quality = "Image quality")
@app_commands.choices(quality=[
    Dalle3Quality(name="Standard", value="standard"),
    Dalle3Quality(name="HD (Finer Details)", value="hd")
])
@app_commands.describe(style = "Image style")
@app_commands.choices(style=[
    Dalle3Style(name="Vivid (Hyper-real)", value="vivid"),
    Dalle3Style(name="Natural (Less hyper-real)", value="natural")
])
async def dalle_3_command(interaction: discord.Interaction, prompt: str, size: app_commands.Choice[str], quality: app_commands.Choice[str], style: app_commands.Choice[str]): # Renamed function
    # Pass validated choices directly using .value
    await handle_dalle_command(interaction, dalle3, prompt, size=size.value, quality=quality.value, style=style.value)


# -------------------------- DALLE 2 ----------------------------------
Dalle2Size = app_commands.Choice

@client.tree.command(name = "dalle_2", description = "Generates an image with DALL-E 2")
@app_commands.describe(prompt = "Describe the image you want DALL-E 2 to create")
@app_commands.describe(size = "Image dimensions")
@app_commands.choices(size=[
    Dalle2Size(name="Small Square (256x256)", value="256x256"),
    Dalle2Size(name="Medium Square (512x512)", value="512x512"),
    Dalle2Size(name="Large Square (1024x1024)", value="1024x1024")
])
async def dalle_2_command(interaction: discord.Interaction, prompt: str, size: app_commands.Choice[str]): # Renamed function
    # Pass validated choice directly using .value
    await handle_dalle_command(interaction, dalle2, prompt, size=size.value)


# --- Main Execution ---
if __name__ == "__main__":
    if not token:
        # This check is redundant if the earlier exit works, but serves as a final safeguard
        logger.critical("Bot token is not configured. Cannot start.")
        sys.exit("Critical Error: Bot token missing.")

    try:
        logger.info("Attempting to start the bot...")
        # Pass the logger instance to client.run if supported by your discord.py version, otherwise use None
        # Check discord.py documentation for the exact signature of client.run regarding logging
        client.run(token, log_handler=None) # Disable default discord.py logging handler if using custom
    except discord.LoginFailure:
        logger.critical("Login Failed: Improper token provided. Check BOT_TOKEN.")
        sys.exit("Critical Error: Invalid bot token.")
    except discord.PrivilegedIntentsRequired as e:
         logger.critical(f"Privileged Intents ({e.shard_id}) are required but not enabled in the Developer Portal.")
         sys.exit("Critical Error: Privileged Intents not enabled.")
    except Exception as e:
        logger.exception("An unexpected error occurred during bot execution:")
        sys.exit("Critical Error: Bot failed to run.")

