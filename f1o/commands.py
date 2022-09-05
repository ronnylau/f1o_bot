import asyncio

import discord
from discord import Activity, ActivityType, Embed, Colour
from discord.ext import commands
from discord.ext import tasks

import logging
import time

from config import PREFIX, VERSION
from f1o import util
from updatechecker.renovate import Renovate
from util import check_f1owebite_status

logger = logging.getLogger(__name__)

# Store the message target
target = None

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True

# Prefix includes the config symbol and the 'f1' name with hard-coded space
bot = commands.Bot(
    command_prefix=f"{PREFIX}f1o ",
    case_insensitive=True,
    intents=intents
)

@bot.event
async def on_ready():
    logger.info('Bot ready...')
    job = Activity(name=bot.command_prefix, type=ActivityType.watching)
    await bot.change_presence(activity=job)
    check_f1_updates.start()

@bot.event
async def on_command_completion(ctx):
    logger.info(f'Command {ctx.prefix}{ctx.command} command complete')


@bot.event
async def on_command_error(ctx, err):
    logger.exception(f'Command failed: {ctx.prefix}{ctx.command}\n {err}')
# Main commands group

# set global time bot started
# store the time as persist in Redis to prevent reset from Dyno refresh
START_TIME = time.time()

def get_uptime():
    """Get running time since bot started. Return tuple (days, hours, minutes)."""
    invoke_time = time.time()
    uptime = invoke_time - START_TIME
    days, rem = divmod(uptime, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    return (int(days), int(hours), int(mins), int(secs))


@bot.command()
async def status(ctx, *args):
    """Get the bot status including uptime, latency and owner."""
    uptime = get_uptime()
    app_info = await bot.application_info()
    latency = int(bot.latency * 1000)

    if bot.is_closed():
        ws_conn = "```glsl\nClosed\n```"
    else:
        ws_conn = "```yaml\nOpen\n```"

    f1o_website_status = await check_f1owebite_status()
    if f1o_website_status == 200:
        f1o_status = "```yaml\nOnline\n```"
    else:
        f1o_status = "```glsl\nOffline\n```"

    embed = Embed(
        title=f"Status - {app_info.name}",
        description=f"{app_info.description}",
        colour=Colour.teal()
    )
    embed.add_field(name='Owner', value=app_info.owner.name, inline=True)
    embed.add_field(name='Version', value=f"{VERSION}", inline=True)
    embed.add_field(name='Ping', value=f'{latency} ms', inline=True)
    embed.add_field(name='Uptime', value=f'{uptime[0]}d, {uptime[1]}h, {uptime[2]}m', inline=True)
    embed.add_field(
        name='Websocket',
        value=ws_conn,
        inline=True
    )
    embed.add_field(name='F1O Website', value=f'{f1o_status}', inline=True)
    await ctx.send(embed=embed)


# Loop commands group
@tasks.loop(seconds=300)
async def check_f1_updates():
    logger.warning('Loop F1 Updates')
    Renovate.Initialize(Renovate)
