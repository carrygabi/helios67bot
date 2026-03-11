import os
import re
import time
import random
import tempfile
import urllib.request
import discord
from discord.ext import commands

# =========================
# CONFIG
# =========================

import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HELIOS_GIF_URLS = [
    "https://media1.tenor.com/m/SJR3O4O8Cn4AAAAd/uma-musume-67.gif",
    "https://media1.tenor.com/m/wKunvSEFCiQAAAAd/uma-musume-tm-opera-o.gif",
    "https://media1.tenor.com/m/c_IrJnrNrksAAAAd/symboli-rudolf-67.gif",
    "https://media1.tenor.com/m/w9wjhtpmH9sAAAAd/uma-musume-uma-musume-meme.gif"
]

# Optional: restrict the bot to one server only.
# Put your server ID here, or leave as 0 to allow all servers.
ALLOWED_GUILD_ID = int(os.getenv("ALLOWED_GUILD_ID", "0"))

# Cooldown per channel in seconds so people can't summon Helios every 0.2 seconds
CHANNEL_COOLDOWN = int(os.getenv("CHANNEL_COOLDOWN", "10"))

# =========================
# DISCORD SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# PATTERNS
# =========================

PATTERN_67 = re.compile(r"(?<!\d)67(?!\d)", re.IGNORECASE)
PATTERN_SIX = re.compile(r"(?<![a-zA-Z0-9])(?:6|six)(?![a-zA-Z0-9])", re.IGNORECASE)
PATTERN_SEVEN = re.compile(r"(?<![a-zA-Z0-9])(?:7|seven)(?![a-zA-Z0-9])", re.IGNORECASE)

last_trigger_time = {}


def should_trigger(content: str) -> bool:
    if PATTERN_67.search(content):
        return True

    has_six = bool(PATTERN_SIX.search(content))
    has_seven = bool(PATTERN_SEVEN.search(content))
    return has_six and has_seven


def is_on_cooldown(channel_id: int) -> bool:
    now = time.time()
    last_time = last_trigger_time.get(channel_id, 0)
    return (now - last_time) < CHANNEL_COOLDOWN


def update_cooldown(channel_id: int) -> None:
    last_trigger_time[channel_id] = time.time()


async def send_gif_as_file(channel: discord.abc.Messageable, gif_url: str) -> None:
    """Download the GIF and upload it as a real file so Discord displays it directly."""
    async with aiohttp.ClientSession() as session:
        async with session.get(gif_url) as response:
            if response.status != 200:
                await channel.send("Helios was summoned, but the GIF could not be downloaded.")
                return

            gif_bytes = await response.read()

    file = discord.File(io.BytesIO(gif_bytes), filename="helios67.gif")
    await channel.send(file=file)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Helios 67 bot is online.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild is None:
        return

    content = message.content.lower()

    if "good morning" in content:
        goldship_url = "https://media1.tenor.com/m/ejfRaXBlY14AAAAd/good-morning-goldship.gif"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as temp_file:
            urllib.request.urlretrieve(goldship_url, temp_file.name)
            temp_path = temp_file.name

        await message.reply(file=discord.File(temp_path), mention_author=False)
        return

    # your 67 logic goes below this
    if should_trigger(content):
        if not is_on_cooldown(message.channel.id):
            update_cooldown(message.channel.id)

            gif_url = random.choice(HELIOS_GIF_URLS)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as temp_file:
                urllib.request.urlretrieve(gif_url, temp_file.name)
                temp_path = temp_file.name

            await message.reply(file=discord.File(temp_path), mention_author=False)

    await bot.process_commands(message)


@bot.command(name="heliostest")
async def helios_test(ctx: commands.Context):
    if HELIOS_GIF_URLS == "PUT_YOUR_GIF_URL_HERE":
        await ctx.send("Set your GIF URL first, you majestic disaster.")
    else:
        await send_gif_as_file(ctx.channel, HELIOS_GIF_URLS)


@bot.command(name="heliosping")
async def helios_ping(ctx: commands.Context):
    await ctx.send("Helios is watching.")


if __name__ == "__main__":
    if TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        raise ValueError("You forgot to set your bot token.")

    bot.run(TOKEN)
