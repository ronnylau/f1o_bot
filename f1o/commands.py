import asyncio

import discord
from discord import Activity, ActivityType, Embed, Colour
from discord.ext import commands
from discord.ext import tasks

import logging
import time

from f1o.config import PREFIX, VERSION, STAGE
from f1o.util import check_f1owebite_status
from updatechecker.renovate import Renovate

logger = logging.getLogger(__name__)

# Store the message target
target = None

intents = discord.Intents.default()
intents.messages = True
intents.members = True
if STAGE == 'DEV':
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


@bot.command()
async def liga(ctx, *args):
    """Get a overview of usefull links based on the league channel (works only i a league-channel)"""
    channelID = ctx.channel.id
    if STAGE == 'DEV':
        if channelID == 927681602081939469:
            await send_league_summary(ctx, 'SIM1')
            await send_league_summary(ctx, 'SIM2')
            await send_league_summary(ctx, 'FH1-100')
            await send_league_summary(ctx, 'FH2-100')
            await send_league_summary(ctx, 'FH3-100')
            await send_league_summary(ctx, 'FH4-100')
            await send_league_summary(ctx, 'FH5-100')
            await send_league_summary(ctx, 'FH6-100')
            await send_league_summary(ctx, 'FH1-50')
            await send_league_summary(ctx, 'FH2-50')
            await send_league_summary(ctx, 'FH3-50')
            await send_league_summary(ctx, 'FH4-50')
            await send_league_summary(ctx, 'FH5-50')
            await send_league_summary(ctx, 'F2-FH1')
            await send_league_summary(ctx, 'F2-FH2')
    else:
        # SIM1
        if channelID == 802273878507388959:
            await send_league_summary(ctx, 'SIM1')
        # SIM2
        elif channelID == 940536923812941874:
            await send_league_summary(ctx, 'SIM2')
        # FH1-100
        elif channelID == 747733037701267499:
            await send_league_summary(ctx, 'FH1-100')
        # FH2-100
        elif channelID == 747733103090466836:
            await send_league_summary(ctx, 'FH2-100')
        # FH3-100
        elif channelID == 747733168387260450:
            await send_league_summary(ctx, 'FH3-100')
        # FH4-100
        elif channelID == 747733240378294292:
            await send_league_summary(ctx, 'FH4-100')
        # FH5-100
        elif channelID == 823677049595363348:
            await send_league_summary(ctx, 'FH5-100')
        # FH6-100
        elif channelID == 871494748983132210:
            await send_league_summary(ctx, 'FH6-100')
        # FH1-50
        elif channelID == 940520492782219284:
            await send_league_summary(ctx, 'FH1-50')
        # FH2-50
        elif channelID == 940520634499350558:
            await send_league_summary(ctx, 'FH2-50')
        # FH3-50
        elif channelID == 940520734357331969:
            await send_league_summary(ctx, 'FH3-50')
        # FH4-50
        elif channelID == 940520917698744340:
            await send_league_summary(ctx, 'FH4-50')
        # FH5-50
        elif channelID == 940521022443106354:
            await send_league_summary(ctx, 'FH5-50')
        # F2-FH1
        elif channelID == 871495307106582629:
            await send_league_summary(ctx, 'F2-FH1')
        # F2-FH2
        elif channelID == 871495388836798485:
            await send_league_summary(ctx, 'F2-FH2')
        #bot-test
        elif channelID == 1015237148577894461:
            await send_league_summary(ctx, 'SIM1')
            await send_league_summary(ctx, 'SIM2')
            await send_league_summary(ctx, 'FH1-100')
            await send_league_summary(ctx, 'FH2-100')
            await send_league_summary(ctx, 'FH3-100')
            await send_league_summary(ctx, 'FH4-100')
            await send_league_summary(ctx, 'FH5-100')
            await send_league_summary(ctx, 'FH6-100')
            await send_league_summary(ctx, 'FH1-50')
            await send_league_summary(ctx, 'FH2-50')
            await send_league_summary(ctx, 'FH3-50')
            await send_league_summary(ctx, 'FH4-50')
            await send_league_summary(ctx, 'FH5-50')
            await send_league_summary(ctx, 'F2-FH1')
            await send_league_summary(ctx, 'F2-FH2')


async def send_league_summary(ctx, liga):
    leagues: Dict[str, Any] = {
        "SIM1": {
            'leagueID': 203,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/28-ps-f1-liga-100/?bundle=SIM%20(1-2)&leagueID=203',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?bundle=SIM%20(1-2)&leagueID=203',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/28-ps-f1-liga-100/?bundle=SIM%20(1-2)&leagueID=203',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?stats=1&leagueID=203',
            'ligaleiter': 'F1O_sf1994',
        },
        "SIM2": {
            'leagueID': 204,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/28-ps-f1-liga-100/?bundle=SIM%20(1-2)&leagueID=204',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?bundle=SIM%20(1-2)&leagueID=204',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/28-ps-f1-liga-100/?bundle=SIM%20(1-2)&leagueID=204',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?stats=1&leagueID=204',
            'ligaleiter': 'Michael_31097',
        },
        "FH1-100": {
            'leagueID': 205,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/28-ps-f1-liga-100/?bundle=FH%20(1-2)&leagueID=205',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?bundle=FH%20(1-2)&leagueID=205',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/28-ps-f1-liga-100/?bundle=FH%20(1-2)&leagueID=205',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?stats=1&leagueID=205',
            'ligaleiter': 'Blanki182',
        },
        "FH2-100": {
            'leagueID': 206,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/28-ps-f1-liga-100/?bundle=FH%20(1-2)&leagueID=206',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?bundle=FH%20(1-2)&leagueID=206',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/28-ps-f1-liga-100/?bundle=FH%20(1-2)&leagueID=206',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?stats=1&leagueID=206',
            'ligaleiter': 'F1O_sf1994',
        },
        "FH3-100": {
            'leagueID': 207,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/28-ps-f1-liga-100/?bundle=FH%20(3-4)&leagueID=207',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?bundle=FH%20(3-4)&leagueID=207',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/28-ps-f1-liga-100/?bundle=FH%20(3-4)&leagueID=207',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?stats=1&leagueID=207',
            'ligaleiter': 'Tobi17662',
        },
        "FH4-100": {
            'leagueID': 208,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/28-ps-f1-liga-100/?bundle=FH%20(3-4)&leagueID=208',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?bundle=FH%20(3-4)&leagueID=208',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/28-ps-f1-liga-100/?bundle=FH%20(3-4)&leagueID=208',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?stats=1&leagueID=208',
            'ligaleiter': 'Why2Jay84',
        },
        "FH5-100": {
            'leagueID': 209,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/28-ps-f1-liga-100/?bundle=FH%20(5-6)&leagueID=209',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?bundle=FH%20(5-6)&leagueID=209',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/28-ps-f1-liga-100/?bundle=FH%20(5-6)&leagueID=209',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?stats=1&leagueID=209',
            'ligaleiter': 'zCrxw02_F1O',
        },
        "FH6-100": {
            'leagueID': 210,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/28-ps-f1-liga-100/?bundle=FH%20(5-6)&leagueID=210',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?bundle=FH%20(5-6)&leagueID=210',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/28-ps-f1-liga-100/?bundle=FH%20(5-6)&leagueID=210',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/28-ps-f1-liga-100/?stats=1&leagueID=210',
            'ligaleiter': 'Michael_31097',
        },
        "FH1-50": {
            'leagueID': 214,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement50/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/29-ps-f1-liga-50/?bundle=FH1&leagueID=214',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?bundle=FH1&leagueID=214',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/29-ps-f1-liga-50/?bundle=FH1&leagueID=214',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?stats=1&leagueID=203',
            'ligaleiter': 'Sexy_Monti',
        },
        "FH2-50": {
            'leagueID': 215,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement50/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/29-ps-f1-liga-50/?bundle=FH%20(2-3)&leagueID=215',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?bundle=FH%20(2-3)&leagueID=215',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/29-ps-f1-liga-50/?bundle=FH%20(2-3)&leagueID=215',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?stats=1&leagueID=215',
            'ligaleiter': 'Daniel_1887',
        },
        "FH3-50": {
            'leagueID': 216,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement50/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/29-ps-f1-liga-50/?bundle=FH%20(2-3)&leagueID=216',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?bundle=FH%20(2-3)&leagueID=216',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/29-ps-f1-liga-50/?bundle=FH%20(2-3)&leagueID=216',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?stats=1&leagueID=216',
            'ligaleiter': 'zCrxw02_F1O',
        },
        "FH4-50": {
            'leagueID': 217,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement50/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/29-ps-f1-liga-50/?bundle=FH%20(4-5)&leagueID=217',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?bundle=FH%20(4-5)&leagueID=217',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/29-ps-f1-liga-50/?bundle=FH%20(4-5)&leagueID=217',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?stats=1&leagueID=217',
            'ligaleiter': 'Sexy_Monti',
        },
        "FH5-50": {
            'leagueID': 218,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f1-reglement50/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/29-ps-f1-liga-50/?bundle=FH%20(4-5)&leagueID=218',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?bundle=FH%20(4-5)&leagueID=218',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/29-ps-f1-liga-50/?bundle=FH%20(4-5)&leagueID=218',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/29-ps-f1-liga-50/?stats=1&leagueID=218',
            'ligaleiter': 'Why2Jay84',
        },
        "F2-FH1": {
            'leagueID': 220,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f2-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/30-ps-f2-liga/?bundle=FH1&leagueID=220',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/30-ps-f2-liga/?bundle=FH1&leagueID=220',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/30-ps-f2-liga/?bundle=FH1&leagueID=220',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/30-ps-f2-liga/?stats=1&leagueID=220',
            'ligaleiter': 'Blanki182',
        },
        "F2-FH2": {
            'leagueID': 221,
            'reglement_URL': 'https://www.f1-onlineliga.com/league/ps-f2-reglement/',
            'SA_URL': 'https://www.f1-onlineliga.com/league/warnings/',
            'cockpits_overview_URL': 'https://www.f1-onlineliga.com/league/cockpits-overview/30-ps-f2-liga/?bundle=FH2&leagueID=221',
            'current_standing_URL': 'https://www.f1-onlineliga.com/league/tables/30-ps-f2-liga/?bundle=FH2&leagueID=221',
            'result_overview_URL': 'https://www.f1-onlineliga.com/league/result-overview/30-ps-f2-liga/?bundle=FH2&leagueID=221',
            'stats_URL': 'https://www.f1-onlineliga.com/league/tables/30-ps-f2-liga/?stats=1&leagueID=221',
            'ligaleiter': 'Daniel_1887',
        }
    }
    if leagues.get(liga):
        currentLeague = leagues.get(liga)
        embed = Embed(
            title=f"Übersicht - {liga}",
            description=f"Hier findest du einige nützliche Links und Informationen für deine Liga.",
            colour=Colour.red()
        )
        embed.add_field(name='Ligaleiter', value=currentLeague['ligaleiter'], inline=False)
        embed.add_field(name='Reglement', value=currentLeague['reglement_URL'], inline=False)
        embed.add_field(name='Strafanträge', value=currentLeague['SA_URL'], inline=False)
        embed.add_field(name='Cockpit-Übersicht', value=currentLeague['cockpits_overview_URL'], inline=False)
        embed.add_field(name='Aktueller Tabellenstand', value=currentLeague['current_standing_URL'], inline=False)
        embed.add_field(name='Ergebnisse der Rennen', value=currentLeague['result_overview_URL'], inline=False)
        embed.add_field(name='Statistiken', value=currentLeague['stats_URL'], inline=False)

        await ctx.send(embed=embed)
    pass


# Loop commands group
@tasks.loop(seconds=300)
async def check_f1_updates():
    if STAGE == 'LIVE':
        logger.warning('Loop F1 Updates')
        Renovate.Initialize(Renovate)
    else:
        pass
