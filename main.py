# Python Modules Go Here
import discord
from discord.ext import commands, tasks
import random
import asyncio
import json
import urllib.parse
from datetime import datetime
import time
import aiohttp
import pytz
import requests
import dbl

# Local Modules Go Here
from opscrape import main as opgrab
from servertime import main as rscheck
from gachacalc import msgsend as hhcalc
from skinscrape import main as getskins
from osuscrape import main as osugrab
from animescrape import main as animgrab
from itunesscrape import main as itunes, lyrics
from maimai import mminfo, mmquery
import cogs.music

# Custom Errors Here


# Initialize Global Variables
_pinfo = {
    "devid": None,
    "debug": None,
    "tz": None
}


f = open("token.txt")
token = f.read()
f.close()


f = open("bottype.txt")
bottype = f.read()
f.close()

with requests.get("http://worldtimeapi.org/api/ip") as r:
    otzdata = r.json()
    _pinfo["tz"] = otzdata["timezone"]


def log(detail: str, ldebug: bool = False):
    if not ldebug:
        logtype = "INFO"
    else:
        logtype = "DEBUG"
    if (not ldebug and not _pinfo["debug"]) or (_pinfo["debug"]):
        print("[" + str(datetime.now()) + "][" + logtype + "] " + detail)


async def aiolog(detail: str, ldebug: bool = False):
    if not ldebug:
        logtype = "INFO"
    else:
        logtype = "DEBUG"
    if (not ldebug and not _pinfo["debug"]) or (_pinfo["debug"]):
        print("[" + str(datetime.now()) + "][" + logtype + "] " + detail)


async def is_dev(ctx):
    return ctx.author.id == _pinfo["devid"].id


if bottype.strip("\n") == "release":
    print("Running Release Code....")
    _pinfo["debug"] = False
    iconlink = "https://img.ezz.moe/0622/17-19-26.png"
elif bottype.strip("\n") == "testing":
    print("Running Development Code....")
    _pinfo["debug"] = True
    iconlink = "https://img.ezz.moe/0622/16-15-14.jpg"


async def bot_prefixes(bot, message):
    bot_id = bot.user.id
    bot_mentions = [f'<@!{bot_id}> ', f'<@{bot_id}> ']
    guild = message.guild

    if bottype.strip("\n") == "release":
        defaultpf = ['e!']
    else:
        defaultpf = ['t!']

    with open("prefixes.json") as f:
        allpf = json.loads(f.read())
    
    if guild:
        try:
            custpf = allpf[str(guild.id)]
        except KeyError:
            return bot_mentions + defaultpf
        else:
            return bot_mentions + [custpf]
    else:
        return bot_mentions + defaultpf

bot = commands.Bot(command_prefix=bot_prefixes)
bot.remove_command('help')


@bot.event
async def on_ready():
    with open("botdb.json") as f:
        botdb = json.load(f)
    print(f'Exusiai is Online! Client name: {bot.user}')
    all_guilds = ""
    guild_count = 0
    for guild in bot.guilds:
        if guild.name == None:
            all_guilds = all_guilds + str(guild.id) + " - ???\n"
        else:
            all_guilds = all_guilds + str(guild.id) + " - " + guild.name + "\n"
        guild_count += 1
    all_guilds = all_guilds.rstrip()
    print(f'Guilds Joined ({str(guild_count)}):\n{all_guilds}')
    _pinfo["devid"] = bot.get_user(256009740239241216)
    print(_pinfo["devid"])
    if bottype.strip("\n") == "release":
        await bot.change_presence(activity=discord.Game(name="e!help | Exusiai"))
        # channel = bot.get_channel(721292304739991552)
        # ResetTime(channel=channel)
        # bot.add_cog(OPbday())         # Deprecating due to possible rewrite
        bot.add_cog(DBLupdate(bot))
    else:
        await bot.change_presence(activity=discord.Game(name="t!help | Exusiai (Dev)"))
        # bot.add_cog(OPbday())         # Deprecating due to possible rewrite
        bot.add_cog(cogs.music)
    await aiolog("The timezone is currently: " + _pinfo["tz"])


async def devreport(command, details: dict):
    embed = discord.Embed(title="Error Details")
    for infotype in details:
        embed.add_field(name=infotype, value=details[infotype])
    await _pinfo["devid"].send("An error has occured in the bot!", embed=embed)


class ResetTime(commands.Cog):
    # pylint: disable=maybe-no-member
    def __init__(self, channel):
        self.timecheck.start(channel=channel)

    def cog_unload(self):
        self.timecheck.cancel()

    @tasks.loop(minutes=5.0)
    async def timecheck(self, channel: discord.VoiceChannel):
        rhour, rmin = await rscheck()
        if int(rhour) == 0:
            rtxt = rmin + "M"
        else:
            rtxt = rhour + "H " + rmin + "M"
        await channel.edit(name=rtxt)

class MTCheck(commands.Cog):
    # pylint: disable=maybe-no-member
    def __init__(self):
        self.mtupdate.start()

    def cog_unload(self):
        self.mtupdate.cancel()

    @tasks.loop(minutes=1.0)
    async def mtupdate(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ezz.moe/arknights?q=maintenance") as r:
                data = await r.json()
                start = data["start"]
                end = data["end"]

        with open("botdb.json") as f:
            funcdata = json.loads(f.read())
        
        startf = pytz.timezone("America/Los_Angeles").localize(datetime.strptime(start, "%Y-%m-%d %H:%M:%S"))
        timeh = pytz.timezone(_pinfo["tz"]).localize(datetime.now())

        if not funcdata["maintain"]:
            if timeh >= startf:
                funcdata["maintain"] = True
                embed = discord.Embed(title="Maintenance Alert", description="The maintenance for the Arknights"
                                                                             " EN Server has started.")
                
                for channel in funcdata["notify"]:
                    smsg = bot.get_channel(channel)


"""
class OPbday(commands.Cog):
    # pylint: disable=maybe-no-member
    def __init__(self):
        log("Starting Birthday Check!")
        self.first = True
        self.bdaycheck.start()
    
    def cog_unload(self):
        self.bdaycheck.cancel()
    
    @tasks.loop(minutes=1.0)
    async def bdaycheck(self):
        with open("botdb.json") as f:
            botdb = json.load(f)
            bday = botdb["opbday"]
        if self.first:
            log("Started Birthday Check!")
            log("opbday key is set to: " + str(bday["alerted"]), True)
            self.first = False
        
        if not bday["alerted"]:
            currtime = pytz.timezone(_pinfo["tz"]).localize(datetime.now()).astimezone(pytz.timezone("America/Los_Angeles"))
            if currtime.hour == 4:
                opnames = ""
                with open("opbday.json") as f:
                    bdayops = json.load(f)
                if str(currtime.day) in bdayops[str(currtime.month)]:
                    for op in bdayops[str(now.month)][str(now.day)]:
                        opnames += " - " + op + "\n"
                    opnames = opnames.strip("\n")
                    embed = discord.Embed(title="Operator Birthday", description="Today is the birthday for:\n" + opnames)
                    embed.set_footer(text="Exusiai", icon_url=iconlink)
                    await aiolog("Server Post Time Now", True)
                    for server in bday["servers"]:
                        log("Server ID: " + str(server), True)
                        for channel in bday["servers"][server]:
                            log("Channel ID for " + server + ": " + str(channel), True)
                            chobj = bot.get_channel(channel)
                            await chobj.send(embed=embed)
                botdb["opbday"]["alerted"] = True
                with open("botdb.json", "w") as f:
                    json.dump(botdb, f, indent=4)
                    log("Finished posting birthday notices")
        else:
            if datetime.now().hour == 0:
                botdb["opbday"]["alerted"] = False
                with open("botdb.json", "w") as f:
                    json.dump(botdb, f, indent=4)
                    log("Recorded as brand new day", True)
"""


class DBLupdate(commands.Cog):
    # pylint: disable=no-method-argument
    def __init__(self, bot):
        self.bot = bot
        with open("topgg.txt") as f:
            self.dbltoken = f.read().strip("\n")
        self.dblpy = dbl.DBLClient(self.bot, self.dbltoken, autopost=True)
    
    async def on_guild_post():
        await aiolog("Discord Bot List: Server count posted successfully")


def stringrip(s: str, cut: str):
    if cut and s.endswith(cut):
        return s[:-len(cut)]


@bot.command()
async def hello(ctx):
    await ctx.send("Yo, Leader!")


# pylint: disable=redefined-builtin
@bot.command()
async def help(ctx):
    umsg = ctx.message
    page = 1
    nochange = True
    first = True
    result = None

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "⬅️️" or "➡️" or "🗑️")

    with open("prefixes.json") as f:
        allpf = json.loads(f.read())
    if ctx.guild:
        try:
            prefix = allpf[str(ctx.guild.id)]
        except KeyError:
            if bottype.strip("\n") == "release":
                prefix = "e!"
            else:
                prefix = "t!"
    else:
        if bottype.strip("\n") == "release":
            prefix = "e!"
        else:
            prefix = "t!"
    
    pages = {"1": ["Arknights (Information)",   "**op [Operator Name]**\n"
                                                "Gives info about the operator (Random if left without an operator name)\n\n"
                                                "**certhh**\n"
                                                "Gives info about getting headhunting tickets using certificates\n\n"
                                                "**banner**\n"
                                                "Gives info for the latest headhunting banner\n\n"
                                                "**event**\n"
                                                "Gives info for the latest event on the EN Server of Arknights\n\n"
                                                "**maintenance**\n"
                                                "Gives info for the latest maintenance schedule\n\n"
                                                "**materials**\n"
                                                "Gives info for farming certain materials (Story levels)"],
            "2": ["Arknights (Misc.)",  "**gacha**\n"
                                        "Simulates a 10x Headhunt based on Arknights chances.\n\n"
                                        "**waifu**\n"
                                        "Gives a random waifu from Arknights!\n\n"
                                        "**husbando**\n"
                                        "Gives a random husbando from Arknights!"],
            "3": ["Other Game Commands",    "**maimai <Song Name>\n**"
                                            "Searches for a Maimai song and returns the info for it!\n\n"
                                            "**olink <Username>**\n"
                                            "Links your Discord username to your osu! username.\n\n"
                                            "**oprofile [Username]**\n"
                                            "Gives info about your player's (or another's) osu! stats. **UNFINISHED**"],
            "4": ["Media Commands", "**anime <Show Name>**\n"
                                    "Gives info about the anime given.\n\n"
                                    "**song <Track Name>**\n"
                                    "Gives info about the song given."],
            "5": ["Misc. Commands", "**support**\n"
                                    "DMs the bot's support server link.\n\n"
                                    "**rng [Initial Range] <Final Range>**\n"
                                    "Gives a random number based on the range.\n\n"
                                    "**prefix** <New Prefix>\n"
                                    "Sets a new prefix for the bot in the server."]}

    while True:
        embed = discord.Embed(title="Exusiai Commands")
        embed.set_thumbnail(url=iconlink)
        embed.description = "Locked and loaded, ready for action!\nWhat's the objective today, Leader?\n\n" \
                            "My prefix is **" + prefix + "**\nSymbols:\n" \
                                                       "[] = Optional (Can be left as empty)\n" \
                                                       "<> = Mandatory (Has to be filled in or else it won't work)"
        embed.add_field(name=pages[str(page)][0], value=pages[str(page)][1])
        
        if first:
            result = await ctx.send(embed=embed)
            await result.add_reaction("⬅️")
            await result.add_reaction("➡️")
            await result.add_reaction("🗑️")
            first = False
        elif not nochange:
            await result.edit(embed=embed)
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await result.clear_reactions()
            return
        else:
            if str(reaction.emoji) == "⬅️":
                await result.remove_reaction("⬅️", umsg.author)
                if page > 1:
                    page -= 1
                    nochange = False
                else:
                    nochange = True
            elif str(reaction.emoji) == "➡️":
                await result.remove_reaction("➡️", umsg.author)
                if page < 5:
                    page += 1
                    nochange = False
                else:
                    nochange = True
            elif str(reaction.emoji) == "🗑️":
                await result.delete()
                await umsg.delete()
                return
                



@bot.command()
@commands.guild_only()
@commands.is_owner()
async def prefix(ctx, newpf):
    with open("prefixes.json") as f:
        allpf = json.loads(f.read())
    with open("prefixes.json", "w") as f:
        allpf[str(ctx.guild.id)] = newpf
        json.dump(allpf, f)
    
    embed = discord.Embed(title="Prefix Changed!", description="Any commands in the server will now use **" \
                                                               + newpf + "** from now on.")
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
async def materials(ctx):
    await ctx.send("__**Simple EN Farming Table**__ (By Cecaniah Corabelle#8846) :\n"
                   "Link : https://imgur.com/dSS1lIB\n\n"
                   "\*This guide as the name implies is just a simple breakdown of the generally most sanity efficient "
                   "maps, however others do exist depending on the sub-drops you may care about. Please look at "
                   "Penguin Statistics (https://penguin-stats.io/) or this spreadsheet ("
                   "https://docs.google.com/spreadsheets/d/12Jwxr5mJBq73z378Bs-C0e6UcPLp-3UmeuSqAH6XmyQ)")


async def delmsg(ctx, umsg, message, timeout: discord.Embed):
    def check(reaction, user):
        return user == umsg.author and str(reaction.emoji) == "🗑️"

    await message.add_reaction("🗑️")

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        timeout.set_author(name="Requested by " + umsg.author.name + "#" + umsg.author.discriminator, icon_url=str(umsg.author.avatar_url))
        await umsg.delete()
        await message.remove_reaction("🗑️", message.author)
        await message.edit(embed=timeout)
    else:
        await umsg.delete()
        await message.delete()


async def timese(start, end):
    ostart = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    oend = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    astart = pytz.timezone("America/Los_Angeles").localize(ostart)
    aend = pytz.timezone("America/Los_Angeles").localize(oend)
    currenttime = pytz.timezone(_pinfo["tz"]).localize(datetime.now())

    async def timecompare(tdelta):
        await aiolog("timecompare reports: " + str(time.strftime('%d %H:%M:%S', time.gmtime(tdelta.total_seconds()))), True)
        if int(time.strftime('%d', time.gmtime(tdelta.total_seconds()))) - 1 >= 1:
            strdur = str(int(time.strftime('%d', time.gmtime(tdelta.total_seconds()))) - 1) + " days"
        elif int(time.strftime('%H', time.gmtime(tdelta.total_seconds()))) >= 1:
            strdur = str(int(time.strftime('%H', time.gmtime(tdelta.total_seconds())))) + " hours"
        elif int(time.strftime('%M', time.gmtime(tdelta.total_seconds()))) >= 1:
            strdur = str(int(time.strftime('%M', time.gmtime(tdelta.total_seconds())))) + " minutes"
        elif int(time.strftime('%S', time.gmtime(tdelta.total_seconds()))) >= 0:
            strdur = str(int(time.strftime('%S', time.gmtime(tdelta.total_seconds())))) + " seconds"
        else:
            strdur = None
        
        return strdur

    if astart < currenttime:
        if aend < currenttime:
            duration = currenttime - aend
            status = "Ended (" + await timecompare(duration) + " ago)"
        else:
            duration = aend - currenttime
            status = "Ongoing (" + await timecompare(duration) + " left)"
    else:
        duration = astart - currenttime
        status = "Not Started (" + await timecompare(duration) + " left)"
    return status


@bot.command()
async def banner(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.ezz.moe/arknights?q=banner") as r:
            bannerdata = await r.json()
    status = await timese(bannerdata["start"], bannerdata["end"])
    embed = discord.Embed(title=bannerdata["title"], description=bannerdata["data"])
    embed.add_field(name="Status", value=status)
    embed.set_image(url=bannerdata["url"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    toembed = discord.Embed(title=bannerdata["title"], description=bannerdata["data"])
    toembed.add_field(name="Status", value=status)
    toembed.set_footer(text="Exusiai", icon_url=iconlink)
    result = await ctx.send(embed=embed)
    await delmsg(ctx, ctx.message, result, toembed)


@bot.command()
async def maintenance(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.ezz.moe/arknights?q=maintenance") as r:
            mtdata = await r.json()
    status = await timese(mtdata["start"], mtdata["end"])
    embed = discord.Embed(title="Maintenance", description=mtdata["data"])
    embed.add_field(name="Status", value=status)
    embed.set_image(url=mtdata["url"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    toembed = discord.Embed(title="Maintenance", description=mtdata["data"])
    toembed.add_field(name="Status", value=status)
    toembed.set_footer(text="Exusiai", icon_url=iconlink)
    result = await ctx.send(embed=embed)
    await delmsg(ctx, ctx.message, result, toembed)


@bot.command()
async def event(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.ezz.moe/arknights?q=event") as r:
            edata = await r.json()
    status = await timese(edata["start"], edata["end"])
    embed = discord.Embed(title="Event", description=edata["data"])
    embed.add_field(name="Status", value=status)
    embed.set_image(url=edata["url"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    toembed = discord.Embed(title="Event")
    toembed.add_field(name="Status", value=status)
    toembed.set_footer(text="Exusiai", icon_url=iconlink)
    result = await ctx.send(embed=embed)
    await delmsg(ctx, ctx.message, result, toembed)


@bot.command()
async def certhh(ctx):
    embed = discord.Embed(title="Headhunting Tickets (Certificates)")
    embed.description = "The \"Headhunting Ticket\" in Advanced Certificate (golden/yellow coloured) shop consists " \
                        "of a few \"steps\"\n\n" \
                        "1 HH ticket = 10 certs\n" \
                        "2 HH ticket = 18 certs\n" \
                        "5 HH ticket = 40 certs\n" \
                        "1 10xHH ticket = 70 certs\n" \
                        "2 10xHH ticket = 120 certs\n\n" \
                        "A total of \"38 pulls\" for a total of 258 certs\n\n" \
                        "**It's only worth it if you're able to buy all the \"steps\".**\n" \
                        "The \"steps\" reset monthly\n\n" \
                        "**How do I get more Advanced Certificates?**\n" \
                        "Store => Certificate => Rules button at bottom"
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
@commands.check(is_dev)
async def test(ctx):
    msg = await ctx.send("Base")
    await msg.add_reaction(":Base:745927609522716713")
    msg = await ctx.send("Elite 1")
    await msg.add_reaction(":Elite_1:745927600416751656")
    msg = await ctx.send("Elite 2")
    await msg.add_reaction(":Elite_2:745926489551405157")
    msg = await ctx.send("Left")
    await msg.add_reaction("⬅️")
    msg = await ctx.send("Right")
    await msg.add_reaction("➡️")


async def opprofile(opstat: dict, woargs: bool):
    opprof = opstat["profile"]
    optags = ""
    for tag in opprof["tags"]:
        optags = optags + tag + ", "
    optags = stringrip(optags, ", ")
    embed = discord.Embed(title=opprof["name"], description=opprof["desc"])
    embed.add_field(name="Profile", value=opprof["fulldesc"], inline=False)
    embed.add_field(name="Quote", value=opprof["quote"], inline=False)
    embed.add_field(name="Archetype", value=opprof["archetype"])
    embed.add_field(name="Tags", value=optags)
    if woargs:
        msgopt = "📂 for full profile\n" \
                 "📋 for operator statistics\n" \
                 "👕 to get the operator's skins\n" \
                 "🌎 to get the web link for more info\n" \
                 "🎲 to re-roll for another operator\n" \
                 "🗑️ to remove this message"
    else:
        msgopt = "📂 for full profile\n" \
                 "📋 for operator statistics\n" \
                 "👕 to get the operator's skins\n" \
                 "🌎 to get the web link for more info\n" \
                 "🗑️ to remove this message"
    embed.add_field(name="Actions", value=msgopt, inline=False)
    embed.set_footer(text="Exusiai", icon_url=iconlink)

    toembed = discord.Embed(title=opprof["name"], description=opprof["desc"])
    toembed.set_footer(text="Exusiai", icon_url=iconlink)

    if opprof["imgurl"] != "???":
        embed.set_image(url=opprof["imgurl"])
        toembed.set_image(url=opprof["imgurl"])
    
    return embed, toembed


async def opdetail(opstat: dict, woargs: bool):
    opprof = opstat["profile"]
    embed = discord.Embed(title=opprof["name"])

    embed.add_field(name="Illustrator", value=opprof["artist"], inline=False)
    embed.add_field(name="CV", value=opprof["cv"], inline=False)

    embed.add_field(name="Gender", value=opprof["gender"], inline=False)
    embed.add_field(name="Place of Birth", value=opprof["PoB"], inline=False)
    embed.add_field(name="Birthday", value=opprof["bday"], inline=False)
    embed.add_field(name="Race", value=opprof["race"], inline=False)
    embed.add_field(name="Height", value=opprof["height"], inline=False)
    embed.add_field(name="Combat Experience", value=opprof["cbex"], inline=False)

    embed.add_field(name="Physical Strength", value=opprof["physstg"], inline=False)
    embed.add_field(name="Mobility", value=opprof["mobile"], inline=False)
    embed.add_field(name="Physiological Endurance", value=opprof["physend"], inline=False)
    embed.add_field(name="Tactical Planning", value=opprof["tactic"], inline=False)
    embed.add_field(name="Combat Skill", value=opprof["cbskill"], inline=False)
    embed.add_field(name="Originium Adaptability", value=opprof["originium"], inline=False)

    if woargs:
        msgopt = "📂 to go back\n" \
                 "📋 for operator statistics\n" \
                 "👕 to get the operator's skins\n" \
                 "🌎 to get the web link for more info\n" \
                 "🎲 to re-roll for another operator\n" \
                 "🗑️ to remove this message"
    else:
        msgopt = "📂 to go back\n" \
                 "📋 for operator statistics\n" \
                 "👕 to get the operator's skins\n" \
                 "🌎 to get the web link for more info\n" \
                 "🗑️ to remove this message"
    embed.add_field(name="Actions", value=msgopt)
    embed.set_footer(text="Exusiai", icon_url=iconlink)

    toembed = discord.Embed(title=opprof["name"])
    toembed.add_field(name="Gender", value=opprof["gender"], inline=False)
    toembed.add_field(name="Place of Birth", value=opprof["PoB"], inline=False)
    toembed.add_field(name="Birthday", value=opprof["bday"], inline=False)
    toembed.add_field(name="Race", value=opprof["race"], inline=False)
    toembed.add_field(name="Height", value=opprof["height"], inline=False)
    embed.set_footer(text="Exusiai", icon_url=iconlink)

    return embed, toembed


async def opstats(message, result: discord.Message, opstat: dict, woargs: bool):
    opprof = opstat["profile"]
    opdata = opstat["stats"]
    first = True
    i = 2
    rank = 4
    if not opdata["e2"]:
        rank = 3

    while True:
        if i == 2:
            oplevel = "Base Max Level"
        elif i == 3:
            oplevel = "Elite 1 Max Level"
        elif i == 4:
            oplevel = "Elite 2 Max Level"

        embed = discord.Embed(title=opprof["name"], description="Operator's Statistics")
        embed.add_field(name="Statistics Level", value=oplevel, inline=False)
        embed.add_field(name="HP", value=opdata["s" + str(i)]["HP"], inline=True)
        embed.add_field(name="ATK", value=opdata["s" + str(i)]["ATK"], inline=True)
        embed.add_field(name="DEF", value=opdata["s" + str(i)]["DEF"], inline=True)
        embed.add_field(name="RES", value=opdata["s" + str(i)]["RES"], inline=True)
        embed.add_field(name="RDP", value=opdata["s" + str(i)]["RDP"], inline=True)
        embed.add_field(name="DP", value=opdata["s" + str(i)]["DP"], inline=True)
        embed.add_field(name="Block", value=opdata["s" + str(i)]["Block"], inline=True)
        embed.add_field(name="ASPD", value=opdata["s" + str(i)]["ASPD"], inline=True)

        await result.edit(embed=embed)
        if first:
            await result.clear_reactions()
            await result.add_reaction(":Base:745927609522716713")
            await result.add_reaction(":Elite_1:745927600416751656")
            await result.add_reaction(":Elite_2:745926489551405157")
            await result.add_reaction("📂")
            await result.add_reaction("🗑️")
            first = False
        
        def check(reaction, user):
            return user == message.author and (str(reaction.emoji) == "<:Base:745927609522716713>" or "<:Elite_1:745927600416751656>" or "<:Elite_2:745926489551405157>" or "📂" or "🗑️")

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await result.clear_reactions()
            return 0
        else:
            if str(reaction.emoji) == "<:Base:745927609522716713>":
                await result.remove_reaction(":Base:745927609522716713", message.author)
                i = 2
            elif str(reaction.emoji) == "<:Elite_1:745927600416751656>":
                await result.remove_reaction(":Elite_1:745927600416751656", message.author)
                i = 3
            elif str(reaction.emoji) == "<:Elite_2:745926489551405157>":
                await result.remove_reaction(":Elite_2:745926489551405157", message.author)
                i = 4
            elif str(reaction.emoji) == "📂":
                await result.clear_reactions()
                i = 8
                return 1
            elif str(reaction.emoji) == "🗑️":
                await result.delete()
                await message.delete()
                i = 9
                return 0


async def aioop(message, operator):
    umsg = message
    ppage = 1
    await aiolog("aioop - operator reported: " + str(operator), True)
    async with message.channel.typing():
        opstat = await opgrab(operator)
        log("opstat reported: " + opstat["search"], True)
        embed, toembed = await opprofile(opstat, operator is None)
    result = await message.channel.send(embed=embed)
    
    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "📂" or "📋" or "👕" or "🌎" or "🎲" or "🗑️")
    
    await result.add_reaction("📂")
    await result.add_reaction("📋")
    await result.add_reaction("👕")
    await result.add_reaction("🌎")
    if operator is None:
        await result.add_reaction("🎲")
    await result.add_reaction("🗑️")

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await result.clear_reactions()
            await result.edit(embed=toembed)
            return
        else:
            if str(reaction.emoji) == "📂":
                await result.remove_reaction("📂", umsg.author)
                if ppage == 1:
                    embed, toembed = await opdetail(opstat, operator is None)
                    ppage = 2
                else:
                    embed, toembed = await opprofile(opstat, operator is None)
                    ppage = 1
                await result.edit(embed=embed)
            elif str(reaction.emoji) == "📋":
                await result.remove_reaction("📋", umsg.author)
                status = await opstats(message, result, opstat, operator is None)
                if status == 1:
                    embed, toembed = await opprofile(opstat, operator is None)
                    await result.edit(embed=embed)

                    await result.add_reaction("📂")
                    await result.add_reaction("📋")
                    await result.add_reaction("👕")
                    await result.add_reaction("🌎")
                    if operator is None:
                        await result.add_reaction("🎲")
                    await result.add_reaction("🗑️")
                elif status == 0:
                    return
            elif str(reaction.emoji) == "👕":
                status = await aioskins(message, result, opstat["profile"]["name"])
                if status == 1:
                    embed, toembed = await opprofile(opstat, operator is None)
                    await result.edit(embed=embed)

                    await result.add_reaction("📂")
                    await result.add_reaction("📋")
                    await result.add_reaction("👕")
                    await result.add_reaction("🌎")
                    if operator is None:
                        await result.add_reaction("🎲")
                    await result.add_reaction("🗑️")
                elif status == 0:
                    return
            elif str(reaction.emoji) == "🌎":
                await umsg.author.send("This is the link for: " + opstat["profile"]["name"] + ".\n" + opstat["profile"]["url"])
                await result.remove_reaction("🌎", umsg.author)
            elif str(reaction.emoji) == "🎲" and operator is None:
                await result.delete()
                await aioop(message, operator)
                return
            elif str(reaction.emoji) == "🗑️":
                await umsg.delete()
                await result.delete()
                return


async def aioskins(message: discord.Message, result: discord.Message, operator: str):
    umsg = message
    first = True
    nochange = True
    opref = False
    opname, imglist = await getskins(operator)
    skincount = len(imglist) - 1
    scroll = 0

    embed = discord.Embed(title="Operator Skins")
    embed.set_author(name=opname)
    embed.set_footer(text="Exusiai", icon_url=iconlink)

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "⬅️" or "➡️" or "📂" or "🗑️")

    while True:
        embed.set_image(url=imglist[scroll])

        if first:
            if result is None:
                result = await message.channel.send(embed=embed)
            else:
                await result.edit(embed=embed)
                opref = True
            await result.clear_reactions()
            await result.add_reaction("⬅️")
            await result.add_reaction("➡️")
            if opref:
                await result.add_reaction("📂")
            await result.add_reaction("🗑️")
            first = False
        elif not nochange:
            await result.edit(embed=embed)

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await result.clear_reactions()
            return
        else:
            if str(reaction.emoji) == "⬅️":
                await result.remove_reaction("⬅️", umsg.author)
                if scroll > 0:
                    scroll -= 1
                    nochange = False
                else:
                    nochange = True
            elif str(reaction.emoji) == "➡️":
                await result.remove_reaction("➡️", umsg.author)
                if not (scroll == skincount):
                    scroll += 1
                    nochange = False
                else:
                    nochange = True
            elif str(reaction.emoji) == "📂":
                await result.remove_reaction("📂", umsg.author)
                if opref:
                    await result.clear_reactions()
                    return 1
            elif str(reaction.emoji) == "🗑️":
                await result.delete()
                await umsg.delete()
                return 0


@bot.command()
async def op(ctx, *, arg: str = None):
    await aioop(ctx.message, arg)


@op.error
async def op_error(ctx, error):
    embed = discord.Embed(title="Error!", description="An error occured in the command!\n"
                                                      "This has been reported to the developer.",
                          color=discord.Colour.red())
    if isinstance(error, ValueError):
        cause = "Unexpected value from operator stats table"
    elif isinstance(error, IndexError):
        cause = "Wrong data grabbed from source"
    elif "NoOperator" in str(error):
        cause = "No operator exists by that name"
    elif "CNOperator" in str(error):
        cause = "That operator has incomplete data"
    else:
        cause = "Error converting data from source"
    embed.add_field(name="Possible Causes", value=cause)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    edetails = {
        "Command Used": "op",
        "Message": ctx.message.content,
        "Error": error
    }
    await devreport("op", edetails)
    await ctx.send(embed=embed)


@bot.command()
async def skins(ctx, *, arg):
    await aioskins(ctx.message, None, arg)


@bot.command()
async def support(ctx):
    user = ctx.author
    await user.send("https://discord.gg/bfbhJvn")
    await ctx.send("The support link is now in your DMs!")


@bot.command()
async def waifu(ctx):
    awaifu = ["Amiya", "Angelina", "Ansel ", "Beagle", "Beehunter", "Blue Poison", "Cardigan", "Catapult", "Cliffheart",
              "Croissant", "Cuora", "DeepColor", "Dobermann", "Durin", "EarthSpirit", "Estelle", "Exusiai",
              "Eyjafjalla",
              "Fang", "Feater", "Firewatch", "Franka", "Frostleaf", "Gavial", "Gitano", "Grani", "Gravel", "Gummy",
              "Haze", "Hibiscus", "Hoshiguma", "Ifrit", "Indra", "Istina", "Jessica", "Kroos", "Lancet-2", "Lappland",
              "Lava", "Liskarmm", "Manticore", "Matoimaru", "Mayer", "Melantha", "Meteorite", "Meteor", "Mousse",
              "Myrrh", "Nearl", "Nightingale", "Nightmare", "Orchid", "Perfumer", "Platinum", "Plume", "Pramanix",
              "Projekt Red ", "Provence", "Ptilopsis", "Rope", "Saria", "Savage", "Scavenger", "Shaw", "Shining",
              "Shirayuki", "Siege", "Silence", "Skadi", "Skyfire", "Sora", "Specter", "Texas", "Vanilla", "Vigna",
              "Vulcan", "Warfarin", "Yato", "Zima"]
    opstat = await opgrab(random.choice(awaifu))
    embed = discord.Embed(title="Waifu Headhunt")
    embed.description = "You got: **" + opstat["profile"]["name"] + "**!"
    embed.set_image(url=opstat["profile"]["imgurl"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
async def husbando(ctx):
    ahusbando = ["12F", "Bison", "Castle-3", "Courier", "Greyy", "Hellagur", "Matterhorn", "Midnight", "Noir Corne",
                 "Ranger", "Steward", "SliverAsh", "Spot"]
    opstat = await opgrab(random.choice(ahusbando))
    embed = discord.Embed(title="Husbando Headhunt")
    embed.description = "You got: **" + opstat["profile"]["name"] + "**!"
    embed.set_image(url=opstat["profile"]["imgurl"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
async def gacha(ctx):
    message = ctx.message
    opmsg = await hhcalc()
    embed = discord.Embed(title="Headhunt Simulator")
    embed.description = "You pulled for 10 operators and:"
    embed.add_field(name="Results", value=opmsg)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    result = await ctx.send(embed=embed)

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) == "🗑️"

    await result.add_reaction("🗑️")

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await result.remove_reaction("🗑️", result.author)
    else:
        await result.delete()
        await message.delete()


@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, player: str, *, reason: str = None):
    uid = int(player.strip("<").strip(">").strip("@").strip("!"))

    try:
        uinfo = await bot.fetch_user(uid)
    except discord.NotFound:
        embed = discord.Embed(title="Command Error!", description="I couldn't get the user that you mentioned!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    except discord.HTTPException:
        embed = discord.Embed(title="Command Error!", description="An error occurred while getting the user's info!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)

    try:
        await ctx.guild.kick(user=uinfo, reason=reason)
    except discord.Forbidden:
        embed = discord.Embed(title="Command Error!", description="My server role does not allow kicking this user!!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    except discord.HTTPException:
        embed = discord.Embed(title="Command Error!", description="An error occurred while kicking the user!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="User Kicked", description="The user has been kicked from this server!")
    embed.add_field(name="User", value=uinfo.mention)
    embed.add_field(name="Kicked by", value=ctx.author.mention)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, player: str, *, reason: str = None):
    uid = int(player.strip("<").strip(">").strip("@").strip("!"))

    try:
        uinfo = await bot.fetch_user(uid)
    except discord.NotFound:
        embed = discord.Embed(title="Command Error!", description="I couldn't get the user that you mentioned!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    except discord.HTTPException:
        embed = discord.Embed(title="Command Error!", description="An error occurred while getting the user's info!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)

    try:
        await ctx.guild.ban(user=uinfo, reason=reason)
    except discord.Forbidden:
        embed = discord.Embed(title="Command Error!", description="My server role does not allow banning this person!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    except discord.HTTPException:
        embed = discord.Embed(title="Command Error!", description="An error occurred while banning the user!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="User Banned", description="The user has been banned from this server!")
    embed.add_field(name="User", value=uinfo.mention)
    embed.add_field(name="Kicked by", value=ctx.author.mention)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, player: str, *, reason: str = None):
    uid = int(player.strip("<").strip(">").strip("@").strip("!"))

    try:
        uinfo = await bot.fetch_user(uid)
    except discord.NotFound:
        embed = discord.Embed(title="Command Error!", description="I couldn't get the user that you mentioned!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    except discord.HTTPException:
        embed = discord.Embed(title="Command Error!", description="An error occurred while getting the user's info!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)

    try:
        await ctx.guild.unban(user=uinfo, reason=reason)
    except discord.Forbidden:
        embed = discord.Embed(title="Command Error!", description="My server role does not allow unbanning this user!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    except discord.HTTPException:
        embed = discord.Embed(title="Command Error!", description="An error occurred while unbanning the player!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="User Unbanned", description="The user has been banned from this server!")
    embed.add_field(name="User", value=uinfo.mention)
    embed.add_field(name="Kicked by", value=ctx.author.mention)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
@commands.is_owner()
async def config(ctx, item: str = None, state: str = True):
    with open("botdb.json") as f:
        botdb = json.load(f)
    
    if not str(ctx.guild.id) in botdb["config"]:
        await aiolog("Creating new entry for new server!", True)
        botdb["config"][str(ctx.guild.id)] = {
            "opparse": True
        }
        with open("botdb.json", "w") as f:
            json.dump(botdb, f, indent=4)

    if item == None:
        allitems = ""
        for item in botdb["config"][str(ctx.guild.id)]:
            allitems = allitems + item + ", "
        allitems = stringrip(allitems, ", ")

        await ctx.send("The configs for this bot are: " + allitems)
    else:
        if state.lower() == "true":
            state = True
        else:
            state = False
        botdb["config"][str(ctx.guild.id)][item] = state
        await aiolog(str(botdb), True)
        with open("botdb.json", "w") as f:
            json.dump(botdb, f, indent=4)
        
        await ctx.send(item + " is now set to: " + str(state))


@bot.command()
async def rng(ctx, fnum: int = 100, lnum: int = None):
    if lnum is None:
        lnum = fnum
        fnum = 0
    value = random.randrange(fnum, lnum)
    await ctx.send("You got: " + str(value))


@rng.error
async def rng_error(ctx, error):
    embed = discord.Embed(title="Error!", description="An error occured in the command!\n"
                                                      "This has been reported to the developer.",
                          color=discord.Colour.red())
    if isinstance(error, discord.ext.commands.BadArgument):
        cause = "The argument given isn't a number!"
    else:
        cause = "Unknown possible causes"
    embed.add_field(name="Possible Causes", value=cause)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await devreport("song", error)
    await ctx.send(embed=embed)


# Media Commands Start Here
@bot.command()
async def anime(ctx, *, showname: str):
    message = ctx.message
    animdat = await animgrab(showname)
    animdat = animdat[0]

    if animdat["airing"]:
        showstat = "Currently Airing"
    else:
        showstat = "Ended"

    embed = discord.Embed(title=animdat["title"])
    embed.add_field(name="Show Status", value=showstat, inline=False)
    embed.add_field(name="Synopsis", value=animdat["synopsis"], inline=False)
    embed.add_field(name="Show Type", value=animdat["type"])
    embed.add_field(name="Episodes", value=animdat["episodes"])
    embed.add_field(name="MAL Score", value=animdat["score"])
    embed.set_thumbnail(url=animdat["image_url"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    result = await ctx.send(embed=embed)

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) == "🗑️"

    await result.add_reaction("🗑️")

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await result.remove_reaction("🗑️", result.author)
    else:
        await result.delete()
        await message.delete()


@anime.error
async def anime_error(ctx, error):
    embed = discord.Embed(title="Error!", description="No anime title was given!",
                          color=discord.Colour.red())
    embed.set_footer(text="Exusiai", icon_url=iconlink)

    await ctx.send(embed=embed)


@bot.command()
async def song(ctx, *, name: str = None):
    umsg = ctx.message
    if name is None:
        embed = discord.Embed(title="Error!", description="No song title was given!",
                          color=discord.Colour.red())
    else:
        data, status = await itunes(name)
        results = data["results"]
        first = results[0]

        if first["trackExplicitness"] == "notExplicit":
            explicit = "Not Explicit"
        else:
            explicit = "Explicit"

        tracktime = datetime.fromtimestamp(int(first["trackTimeMillis"])/1000.0)
        trackdur = tracktime - datetime.fromtimestamp(0)
        trackhour = time.strftime('%H', time.gmtime(int(trackdur.total_seconds())))

        if int(trackhour) > 0:
            trackstamp = time.strftime('%H:%M:%S', time.gmtime(int(trackdur.total_seconds())))
        else:
            trackstamp = time.strftime('%M:%S', time.gmtime(int(trackdur.total_seconds())))

        embed = discord.Embed(title=first["trackName"], description="by " + first["artistName"])
        embed.add_field(name="Album", value=first["collectionName"], inline=False)
        embed.add_field(name="Explicit Status", value=explicit)
        embed.add_field(name="Genre", value=first["primaryGenreName"])
        embed.add_field(name="Track Duration", value=str(trackstamp))
        embed.set_thumbnail(url=first["artworkUrl100"])

    embed.set_footer(text="Exusiai", icon_url=iconlink)
    result = await ctx.send(embed=embed)

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "📄" or "🗑️")

    await result.add_reaction("📄")
    await result.add_reaction("🗑️")

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await result.remove_reaction("📄", result.author)
        await result.remove_reaction("🗑️", result.author)
    else:
        if str(reaction.emoji) == "📄":
            await result.delete()
            await lyric(ctx, name)
        else:
            await result.delete()
            await umsg.delete()


@song.error
async def song_error(ctx, error):
    embed = discord.Embed(title="Error!", description="An error occured in the command!\n"
                                                      "This has been reported to the developer.",
                          color=discord.Colour.red())
    if isinstance(error, IndexError):
        cause = "No songs by given name"
    else:
        cause = "Unknown possible causes"
    embed.add_field(name="Possible Causes", value=cause)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await devreport("song", error)
    await ctx.send(embed=embed)


@bot.command()
async def lyric(context, name: str = None):
    umsg = context.message
    data, status = await itunes(name)
    results = data["results"]
    first = results[0]
    async with context.typing():
        songlyric = await lyrics(name)

    embed = discord.Embed(title=first["trackName"], description="by " + first["artistName"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await context.send(embed=embed)
    await context.send(songlyric)


@lyric.error
async def lyric_error(ctx, error):
    embed = discord.Embed(title="Error!", description="An error occured in the command!\n"
                                                      "This has been reported to the developer.",
                          color=discord.Colour.red())
    if isinstance(error, IndexError):
        cause = "No lyrics by given name"
    else:
        cause = "Unknown possible causes"
    embed.add_field(name="Possible Causes", value=cause)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await devreport("lyric", error)
    await ctx.send(embed=embed)


# Maimai Command Starts Here
@bot.command()
async def maimai(ctx, *, song: str = ""):
    umsg = ctx.message
    if song == "":
        embed = discord.Embed(title="Error!", description="No song title was given!",
                          color=discord.Colour.red())
        await ctx.send(embed=embed)
    else:
        async with ctx.channel.typing():
            songlist = await mmquery(song)
            i = 1
            lsong = ""
            for name in songlist["names"]:
                lsong += str(i) + ". " + name + "\n"
                i += 1
            schoice = discord.Embed(title="Search Results", description="Choose a song below.")
            schoice.add_field(name="Results", value=lsong.strip())
            schoice.add_field(name="Other Actions", value="Enter 'cancel' to cancel the command.")
            schoice.set_footer(text="Exusiai", icon_url=iconlink)

        mainmsg = await ctx.send(embed=schoice)

        def msg_check(m):
            return m.channel == ctx.channel and m.author.id == umsg.author.id

        while True:
            try:
                msg = await bot.wait_for('message', timeout=30.0, check=msg_check)
            except asyncio.TimeoutError:
                toembed = discord.Embed(title="Timeout!", description="No song title was given within 30 seconds.",
                                        color=discord.Colour.red())
                await mainmsg.edit(embed=toembed)
                await asyncio.sleep(3)
                return
            else:
                try:
                    choicenum = int(msg.content)
                except TypeError:
                    if choicenum == "cancel":
                        await msg.delete()
                        await mainmsg.delete()
                        await ctx.message.delete()
                        return
                    else:
                        schoice = discord.Embed(title="Search Results", description="Not a valid choice!\nChoose a song below.", color=discord.Colour.red())
                        schoice.add_field(name="Results", value=lsong.strip())
                        schoice.add_field(name="Other Actions", value="Enter 'cancel' to cancel the command.")
                        schoice.set_footer(text="Exusiai", icon_url=iconlink)
                        await msg.delete()
                        await mainmsg.edit(embed=schoice)
                else:
                    if choicenum <= len(songlist["names"]):
                        async with ctx.channel.typing():
                            mmdata = await mminfo(songlist["links"][choicenum - 1])
                            result = discord.Embed(title=mmdata["jpname"])
                            if mmdata["enname"] != mmdata["jpname"]:
                                result.add_field(name="Name (Japanese)", value=mmdata["jpname"])
                                result.add_field(name="Name (English)", value=mmdata["enname"])
                            else:
                                result.add_field(name="Name", value=mmdata["jpname"])
                            if mmdata["enartist"] != mmdata["jpartist"]:
                                result.add_field(name="Artist (Japanese)", value=mmdata["jpartist"])
                                result.add_field(name="Artist (English)", value=mmdata["enartist"])
                            else:
                                result.add_field(name="Artist", value=mmdata["jpartist"])
                            result.add_field(name="Category", value=mmdata["category"])
                            result.add_field(name="First Release", value=mmdata["release"])
                            result.add_field(name="Release Date", value=mmdata["date"])
                            result.add_field(name="BPM", value=mmdata["bpm"])
                            if mmdata["intl"]:
                                result.add_field(name="Intl. Version Availability", value="Yes", inline=False)
                            elif not mmdata["intl"]:
                                result.add_field(name="Intl. Version Availability", value="No", inline=False)
                            if mmdata["diffs"] != []:
                                diffstr = ""
                                for diff in mmdata["diffs"]:
                                    diffstr += diff + ", "
                                result.add_field(name="Difficulty Levels for: " + mmdata["diffplatform"], value=diffstr.strip(", "), inline=False)
                            result.set_thumbnail(url=mmdata["image"])
                            result.set_footer(text="Exusiai", icon_url=iconlink)
                            await msg.delete()

                        await mainmsg.edit(embed=result)
                        return



# Osu Commands Start Here
async def playerdb(player: int, mode: str = "read", uname: str = None):
    f = open("osuplayer.json")
    filedata = f.read()
    f.close()
    data = json.loads(filedata)

    if mode == "read":
        try:
            username = data[str(player)]
            done = True
        except KeyError:
            username = None
            done = False
        return username, done
    elif mode == "write":
        data[str(player)] = uname
        fwrite = json.dumps(data)
        f = open("osuplayer.json", "w")
        f.write(fwrite)
        f.close()
        return uname, True


@bot.command()
async def olink(ctx, player: str):
    await playerdb(ctx.author.id, "write", player)
    embed = discord.Embed(title="osu! Account Linked!",
                          description="Your Discord is now linked to: " + player)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
async def oprofile(ctx, player: str = None, mode: str = "std"):
    if player is None:
        uname, status = await playerdb(ctx.author.id)
    else:
        uname = player            
    if not status:
        uname = ctx.author.name
    info, stat = await osugrab(uname)
    if stat:
        embed = discord.Embed(title=info["username"],
                                description="Current Ranking: #" + info["pp_rank"] \
                                + " (" + info["country"] + " #" + info["pp_country_rank"] + ")")
        embed.add_field(name="Ranked Score", value=info["ranked_score"])
        embed.add_field(name="Performance Points", value=info["pp_raw"] + "pp")
    else:
        embed = discord.Embed(title="Error!", description="No account found by the name " + uname + "!")

    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
@commands.check(is_dev)
async def serverlist(ctx):
    guildstr = ""
    allguildarr = []
    all_guilds = ""
    guild_count = 0
    guildarrcount = 0
    for guild in bot.guilds:
        guildstr = guildstr + str(guild.id) + " - " + guild.name + "\n"
        guildarrcount += 1
        if guildarrcount == 30:
            allguildarr.append(guildstr)
            guildstr = ""
        guild_count += 1
    if guildstr != "":
        allguildarr.append(guildstr)
    await ctx.send("Servers joined (" + str(guild_count) + "):")
    for guild in allguildarr:
        guildsend = guild.rstrip()
        await ctx.send(guildsend)


@bot.command()
@commands.is_owner()
async def opnotify(ctx):
    with open("botdb.json") as f:
        botdb = json.load(f)
    


@bot.command()
@commands.check(is_dev)
async def botdebug(ctx):
    if not _pinfo["debug"]:
        _pinfo["debug"] = True
        log("Debug mode is now enabled!")
        await ctx.send("Debug mode is now enabled.")
    else:
        _pinfo["debug"] = False
        log("Debug mode is now disabled!")
        await ctx.send("Debug mode is now disabled.")


@bot.event
async def on_message(message):
    if message.guild and message.author.id != bot.user.id:
        with open("prefixes.json") as f:
            prefixes = json.load(f)
        bot_id = bot.user.id
        bot_mentions = [f'<@!{bot_id}> ', f'<@{bot_id}> ']
        servcmd = False
        
        try:
            bot_mentions.append(prefixes[str(message.guild.id)])
        except KeyError:
            if bottype.strip("\n") == "release":
                bot_mentions.append("e!")
            else:
                bot_mentions.append("t!")
        
        for mention in bot_mentions:
            if mention in message.content:
                servcmd = True
                await aiolog("This is a command! Not parsing the whole message.", True)

        await aiolog("servcmd reports: " + str(servcmd), True)
        if not servcmd:
            with open("botdb.json") as f:
                botdb = json.load(f)
            if str(message.guild.id) in botdb["config"]:
                await aiolog("Loading existing entry from database...", True)
                botconfig = botdb["config"][str(message.guild.id)]
            else:
                await aiolog("Creating new entry for new server!", True)
                botdb["config"][str(message.guild.id)] = {
                    "opparse": True
                }
                botconfig = botdb["config"][str(message.guild.id)]
                with open("botdb.json", "w") as f:
                    json.dump(botdb, f, indent=4)
            if ("https://gamepress.gg/arknights/operator/" in message.content) and botconfig["opparse"]:
                opname = message.content.replace("https://gamepress.gg/arknights/operator", "").replace("-", " ")
                await aioop(message, opname)

        await bot.process_commands(message)


bot.run(token)
