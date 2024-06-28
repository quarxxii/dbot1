import discord
from discord.ext import commands, tasks
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CMD_CHANNEL_NAME = 'cmd'  # Update this to your actual command channel name

# Load keys from the JSON file
def load_keys():
    try:
        if not os.path.exists('keys.json'):
            return []
        with open('keys.json', 'r') as f:
            keys = json.load(f)
            print(f"Loaded keys: {keys}")  # Debug statement
            return keys
    except Exception as e:
        print(f"Error loading keys: {e}")
        return []

# Save keys to the JSON file
def save_keys(keys):
    try:
        with open('keys.json', 'w') as f:
            json.dump(keys, f)
            print(f"Saved keys: {keys}")  # Debug statement
    except Exception as e:
        print(f"Error saving keys: {e}")

# Load assigned keys from the JSON file
def load_assigned_keys():
    try:
        if not os.path.exists('assigned_keys.json'):
            return {}
        with open('assigned_keys.json', 'r') as f:
            assigned_keys = json.load(f)
            print(f"Loaded assigned keys: {assigned_keys}")  # Debug statement
            return assigned_keys
    except Exception as e:
        print(f"Error loading assigned keys: {e}")
        return {}

# Save assigned keys to the JSON file
def save_assigned_keys(assigned_keys):
    try:
        with open('assigned_keys.json', 'w') as f:
            json.dump(assigned_keys, f)
            print(f"Saved assigned keys: {assigned_keys}")  # Debug statement
    except Exception as e:
        print(f"Error saving assigned keys: {e}")

@bot.command(name='getkey')
async def get_key(ctx):
    user_id = str(ctx.author.id)
    keys = load_keys()
    assigned_keys = load_assigned_keys()

    if user_id in assigned_keys:
        await ctx.author.send("You have already received a key.")
        return

    if not keys:
        await ctx.author.send("No more keys available.")
        return

    key = keys.pop(0)
    assigned_keys[user_id] = key

    save_keys(keys)
    save_assigned_keys(assigned_keys)

    await ctx.author.send(f"Here is your key: {key}")
    await update_cmd_channel(ctx.guild)

@bot.command(name='forgotkey')
async def forgot_key(ctx):
    user_id = str(ctx.author.id)
    assigned_keys = load_assigned_keys()

    if user_id not in assigned_keys:
        await ctx.author.send("You have not requested a key yet.")
        return

    key = assigned_keys[user_id]
    await ctx.author.send(f"Your key is: {key}")

@bot.command(name='createkey')
@commands.has_permissions(administrator=True)
async def create_key(ctx, *, keys: str):
    keys_list = [key.strip() for key in keys.split(',')]
    existing_keys = load_keys()
    existing_keys.extend(keys_list)
    save_keys(existing_keys)
    await ctx.send(f"Keys '{', '.join(keys_list)}' have been added.")
    await update_cmd_channel(ctx.guild)

@create_key.error
async def create_key_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if message.channel.name == CMD_CHANNEL_NAME:
        await message.delete(delay=10)

@bot.event
async def on_ready():
    update_cmd_channel_task.start()
    print(f'Bot is ready. Logged in as {bot.user}')

async def update_cmd_channel(guild):
    cmd_channel = discord.utils.get(guild.channels, name=CMD_CHANNEL_NAME)
    if cmd_channel:
        keys = load_keys()
        remaining_keys = len(keys)

        embed = discord.Embed(title="Command Center", color=discord.Color.blue())
        embed.add_field(name="Remaining keys", value=f"{remaining_keys}", inline=False)
        embed.add_field(name="!getkey", value="Request a key", inline=False)
        embed.add_field(name="!forgotkey", value="Retrieve your requested key", inline=False)

        async for message in cmd_channel.history(limit=10):
            if message.author == bot.user:
                await message.edit(embed=embed)
                return
        await cmd_channel.send(embed=embed)

@tasks.loop(minutes=1)
async def update_cmd_channel_task():
    try:
        for guild in bot.guilds:
            await update_cmd_channel(guild)
    except Exception as e:
        print(f"Unhandled exception in update_cmd_channel_task: {e}")

# Run the bot
bot.run('MTA4NjgwODA3MzEzOTY1ODg0Mw.GJ-siw.kXEr2nHLcbmpUN3C_AM4b_ktQvLIRN2tgTc0T4')  # Ersetzen Sie YOUR_BOT_TOKEN durch Ihren tatsächlichen Bot-Token



