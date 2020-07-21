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

# Local Modules Go Here
from opscrape import main as opgrab
from servertime import main as rscheck
from gachacalc import msgsend as hhcalc
from skinscrape import main as getskins
from osuscrape import main as osugrab
from animescrape import main as animgrab
from itunesscrape import main as itunes, lyrics


f = open("token.txt")
token = f.read()
f.close()


f = open("bottype.txt")
bottype = f.read()
f.close()


if bottype.strip("\n") == "release":
    print("Running Release Code....")
    iconlink = "https://img.ezz.moe/0622/17-19-26.png"
elif bottype.strip("\n") == "testing":
    print("Running Development Code....")
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
    global botdb
    with open("botdb.json") as f:
        botdb = json.load(f)
    print(f'Exusiai is Online! Client name: {bot.user}')
    all_guilds = ""
    guild_count = 0
    for guild in bot.guilds:
        all_guilds = all_guilds + str(guild.id) + " - " + guild.name + "\n"
        guild_count += 1
    all_guilds = all_guilds.rstrip()
    print(f'Guilds Joined ({str(guild_count)}):\n{all_guilds}')
    global devid
    devid = bot.get_user(256009740239241216)
    if bottype.strip("\n") == "release":
        await bot.change_presence(activity=discord.Game(name="e!help | Exusiai"))
        channel = bot.get_channel(721292304739991552)
        ResetTime(channel=channel)
    else:
        await bot.change_presence(activity=discord.Game(name="t!help | Exusiai (Dev)"))


async def devreport(command, error):
    embed = discord.Embed(title="Error Details")
    embed.add_field(name="Command Used", value=command, inline=False)
    embed.add_field(name="Message", value=error, inline=False)
    await devid.send("An error has occured in the bot!", embed=embed)


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
        timeh = pytz.timezone("Asia/Kuala_Lumpur").localize(datetime.now())

        if funcdata["maintain"] == False:
            if timeh >= startf:
                funcdata["maintain"] = True
                embed = discord.Embed(title="Maintenance Alert", description="The maintenance for the Arknights"
                                                                             " EN Server has started.")
                
                for channel in funcdata["notify"]:
                    smsg = bot.get_channel(channel)


def stringrip(s: str, cut: str):
    if cut and s.endswith(cut):
        return s[:-len(cut)]


@bot.command()
async def hello(ctx):
    await ctx.send("Yo, Leader!")


@bot.command()
async def help(ctx):
    umsg = ctx.message
    page = 1

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "⬅" or "➡" or "🗑️")

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

    while True:
        embed = discord.Embed(title="Exusiai Commands")
        embed.set_thumbnail(url=iconlink)
        embed.description = "Locked and loaded, ready for action!\nWhat's the objective today, Leader?\n\n" \
                            "My prefix is **" + prefix + "**\nSymbols:\n" \
                                                       "[] = Optional (Can be left as empty)\n" \
                                                       "<> = Mandatory (Has to be filled in or else it won't work)"
        if page == 1:
            embed.add_field(name="Actions", value="⬅ for previous page\n\n"
                                                  "➡ for next page\n\n"
                                                  "🗑️ to delete the help message")
            hmsg = await ctx.send(embed=embed)

            await hmsg.add_reaction("➡")
            await hmsg.add_reaction("🗑️")

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await hmsg.remove_reaction("➡", hmsg.author)
                await hmsg.remove_reaction("🗑️", hmsg.author)
                return
            else:
                if str(reaction.emoji) == "🗑️":
                    await hmsg.delete()
                    await umsg.delete()
                    return
                else:
                    await hmsg.delete()
                    page += 1
        elif page == 2:
            embed.add_field(name="Arknights (Information)",
                            value="**op [Operator Name]**\n"
                                  "Gives info about the operator (Random if left without an operator name)\n\n"
                                  "**certhh**\n"
                                  "Gives info about getting headhunting tickets using certificates\n\n"
                                  "**banner**\n"
                                  "Gives info for the latest headhunting banner\n\n"
                                  "**event**\n"
                                  "Gives info for the latest event on the EN Server of Arknights"
                                  "**maintenance**\n"
                                  "Gives info for the latest maintenance schedule\n\n"
                                  "**materials**\n"
                                  "Gives info for farming certain materials (Story levels)",
                            inline=False)
            hmsg = await ctx.send(embed=embed)

            await hmsg.add_reaction("⬅")
            await hmsg.add_reaction("➡")
            await hmsg.add_reaction("🗑️")

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await hmsg.remove_reaction("⬅", hmsg.author)
                await hmsg.remove_reaction("➡", hmsg.author)
                await hmsg.remove_reaction("🗑️", hmsg.author)
                return
            else:
                if str(reaction.emoji) == "⬅":
                    await hmsg.delete()
                    page -= 1
                elif str(reaction.emoji) == "➡":
                    await hmsg.delete()
                    page += 1
                elif str(reaction.emoji) == "🗑️":
                    await hmsg.delete()
                    await umsg.delete()
                    return
        elif page == 3:
            embed.add_field(name="Arknights (Misc.)",
                            value="**gacha**\n"
                                  "Simulates a 10x Headhunt based on Arknights chances.\n\n"
                                  "**waifu**\n"
                                  "Gives a random waifu from Arknights!\n\n"
                                  "**husbando**\n"
                                  "Gives a random husbando from Arknights!")
            hmsg = await ctx.send(embed=embed)

            await hmsg.add_reaction("⬅")
            await hmsg.add_reaction("➡")
            await hmsg.add_reaction("🗑️")

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await hmsg.remove_reaction("⬅", hmsg.author)
                await hmsg.remove_reaction("➡", hmsg.author)
                await hmsg.remove_reaction("🗑️", hmsg.author)
                return
            else:
                if str(reaction.emoji) == "⬅":
                    await hmsg.delete()
                    page -= 1
                elif str(reaction.emoji) == "➡":
                    await hmsg.delete()
                    page += 1
                if str(reaction.emoji) == "🗑️":
                    await hmsg.delete()
                    await umsg.delete()
                    return
        elif page == 4:
            embed.add_field(name="Other Game Commands",
                            value="**olink <Username>**\n"
                                  "Links your Discord username to your osu! username.\n\n"
                                  "**oprofile [Username]**\n"
                                  "Gives info about your player's (or another's) osu! stats")
            hmsg = await ctx.send(embed=embed)

            await hmsg.add_reaction("⬅")
            await hmsg.add_reaction("➡")
            await hmsg.add_reaction("🗑️")

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await hmsg.remove_reaction("⬅", hmsg.author)
                await hmsg.remove_reaction("➡", hmsg.author)
                await hmsg.remove_reaction("🗑️", hmsg.author)
                return
            else:
                if str(reaction.emoji) == "⬅":
                    await hmsg.delete()
                    page -= 1
                elif str(reaction.emoji) == "➡":
                    await hmsg.delete()
                    page += 1
                if str(reaction.emoji) == "🗑️":
                    await hmsg.delete()
                    await umsg.delete()
                    return
        elif page == 5:
            embed.add_field(name="Media Commands",
                            value="**anime <Show Name>**\n"
                                  "Gives info about the anime given.\n\n"
                                  "**song <Track Name>**\n"
                                  "Gives info about the song given.")
            hmsg = await ctx.send(embed=embed)

            await hmsg.add_reaction("⬅")
            await hmsg.add_reaction("➡")
            await hmsg.add_reaction("🗑️")

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await hmsg.remove_reaction("⬅", hmsg.author)
                await hmsg.remove_reaction("➡", hmsg.author)
                await hmsg.remove_reaction("🗑️", hmsg.author)
                return
            else:
                if str(reaction.emoji) == "⬅":
                    await hmsg.delete()
                    page -= 1
                elif str(reaction.emoji) == "➡":
                    await hmsg.delete()
                    page += 1
                if str(reaction.emoji) == "🗑️":
                    await hmsg.delete()
                    await umsg.delete()
                    return
        elif page == 6:
            embed.add_field(name="Misc. Commands",
                            value="**rng [Initial Range] <Final Range>**\n"
                                  "Gives a random number based on the range.\n\n"
                                  "**prefix** <New Prefix>\n"
                                  "Sets a new prefix for the bot in the server.")
            hmsg = await ctx.send(embed=embed)

            await hmsg.add_reaction("⬅")
            await hmsg.add_reaction("➡")
            await hmsg.add_reaction("🗑️")

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await hmsg.remove_reaction("⬅", hmsg.author)
                await hmsg.remove_reaction("➡", hmsg.author)
                await hmsg.remove_reaction("🗑️", hmsg.author)
                return
            else:
                if str(reaction.emoji) == "⬅":
                    await hmsg.delete()
                    page -= 1
                elif str(reaction.emoji) == "➡":
                    await hmsg.delete()
                    page += 1
                if str(reaction.emoji) == "🗑️":
                    await hmsg.delete()
                    await umsg.delete()
                    return
        elif page == 7:
            embed.add_field(name="Moderation (WIP)",
                            value="**mute <User> [Reason]**\n"
                                  "Mutes a user in the server\n\n"
                                  "**unmute <User> [Reason]**\n"
                                  "Unmutes a currently muted user\n\n"
                                  "**kick <User> [Reason]**\n"
                                  "Kicks a user in the server\n\n"
                                  "**ban <User> [Reason]**\n"
                                  "Bans a user in the server\n\n"
                                  "**unban <User> [Reason]**\n"
                                  "Unbans a user that was previously banned",
                            inline=False)
            hmsg = await ctx.send(embed=embed)

            await hmsg.add_reaction("⬅")
            await hmsg.add_reaction("🗑️")

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await hmsg.remove_reaction("⬅", hmsg.author)
                await hmsg.remove_reaction("🗑️", hmsg.author)
                return
            else:
                if str(reaction.emoji) == "🗑️":
                    await hmsg.delete()
                    await umsg.delete()
                    return
                else:
                    await hmsg.delete()
                    page -= 1


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


async def delmsg(ctx, umsg, message):
    def check(reaction, user):
        return user == umsg.author and str(reaction.emoji) == "🗑️"

    await message.add_reaction("🗑️")

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await umsg.delete()
        await message.delete()
    else:
        await umsg.delete()
        await message.delete()


@bot.command()
async def banner(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.ezz.moe/arknights?q=banner") as r:
            bannerdata = await r.json()
    embed = discord.Embed(title=bannerdata["title"], description=bannerdata["data"])
    embed.set_image(url=bannerdata["url"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    result = await ctx.send(embed=embed)
    await delmsg(ctx, ctx.message, result)


async def timese(start, end):
    start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    if start < datetime.now():
        if end < datetime.now():
            status = "Ended"
        else:
            status = "Ongoing"
    else:
        status = "Not Started"
    return status


@bot.command()
async def maintenance(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.ezz.moe/arknights?q=maintenance") as r:
            mtdata = await r.json()
    status = await timese(mtdata["start"], mtdata["end"])
    embed = discord.Embed(title="Maintenance", description=mtdata["data"])
    embed.add_field(name="Status", value=status)
    embed.set_image(url=mtdata["url"])
    result = await ctx.send(embed=embed)
    await delmsg(ctx, ctx.message, result)


@bot.command()
async def event(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.ezz.moe/arknights?q=event") as r:
            edata = await r.json()
    status = await timese(edata["start"], edata["end"])
    embed = discord.Embed(title="Event", description=edata["data"])
    embed.add_field(name="Status", value=status)
    embed.set_image(url=edata["url"])
    result = await ctx.send(embed=embed)
    await delmsg(ctx, ctx.message, result)


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
async def test(ctx):
    umsg = ctx.message
    message = await ctx.send("**Thisisaline**,\nThisislinetwo")
    print(type(message))
    print(message)

    await delmsg(ctx, umsg, message)


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
    if opprof["imgurl"] != "???":
        embed.set_image(url=opprof["imgurl"])
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    
    return embed


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
                 "🌎 to get the web link for more info" \
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

    return embed
    

async def opstats(message, result: discord.Message, opstat: dict, woargs: bool):
    opprof = opstat["profile"]
    opdata = opstat["stats"]
    first = True
    i = 1
    rank = 4
    if not opdata["e2"]:
        rank = 3
    
    while True:
        await result.delete()

        if i == 1:
            oplevel = "Base Min Level"
        elif i == 2:
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

        msgopt = "📂 to go back\n" \
                 "🗑️ to remove this message"

        embed.add_field(name="Actions", value=msgopt, inline=False)
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        result = await message.channel.send(embed=embed)

        if i > 1:
            await result.add_reaction("⬅")
        if i < rank:
            await result.add_reaction("➡")
        await result.add_reaction("📂")
        await result.add_reaction("🗑️")

        def check(reaction, user):
            return user == message.author and (str(reaction.emoji) == "⬅" or "➡" or "📂" or "🗑️")
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            if i > 1:
                await result.remove_reaction("⬅", result.author)
            if i < rank:
                await result.remove_reaction("➡", result.author)
            await result.remove_reaction("📂", result.author)
            await result.remove_reaction("🗑️", result.author)
            return 0
        else:
            if str(reaction.emoji) == "⬅" and i > 1:
                await result.remove_reaction("⬅", message.author)
                i -= 1
            elif str(reaction.emoji) == "➡" and i < rank:
                await result.remove_reaction("➡", message.author)
                i += 1
            elif str(reaction.emoji) == "📂":
                await result.delete()
                return 1
            elif str(reaction.emoji) == "🗑️":
                await result.delete()
                await message.delete()
                return 0


async def aioop(message, operator):
    umsg = message
    ppage = 1
    async with message.channel.typing():
        opstat = await opgrab(operator)
        embed = await opprofile(opstat, operator == None)
    result = await message.channel.send(embed=embed)
    
    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "📂" or "📋" or "👕" or "🌎" or "🎲" or "🗑️")
    
    await result.add_reaction("📂")
    await result.add_reaction("📋")
    await result.add_reaction("👕")
    await result.add_reaction("🌎")
    if operator == None:
        await result.add_reaction("🎲")
    await result.add_reaction("🗑️")

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await result.remove_reaction("📂", result.author)
            await result.remove_reaction("📋", result.author)
            await result.remove_reaction("👕", result.author)
            await result.remove_reaction("🌎", result.author)
            if operator == None:
                await result.remove_reaction("🎲", result.author)
            await result.remove_reaction("🗑️", result.author)
            return
        else:
            if str(reaction.emoji) == "📂":
                await result.remove_reaction("📂", umsg.author)
                if ppage == 1:
                    embed = await opdetail(opstat, operator == None)
                    ppage = 2
                else:
                    embed = await opprofile(opstat, operator == None)
                    ppage = 1
                await result.edit(embed=embed)
            elif str(reaction.emoji) == "📋":
                await result.remove_reaction("📋", umsg.author)
                status = await opstats(message, result, opstat, operator == None)
                if status == 1:
                    embed = await opprofile(opstat, operator == None)
                    result = await message.channel.send(embed=embed)

                    await result.add_reaction("📂")
                    await result.add_reaction("📋")
                    await result.add_reaction("👕")
                    await result.add_reaction("🌎")
                    if operator == None:
                        await result.add_reaction("🎲")
                    await result.add_reaction("🗑️")
                elif status == 0:
                    return
            elif str(reaction.emoji) == "👕":
                await result.delete()
                await aioskins(message, opstat["profile"]["name"])
                return
            elif str(reaction.emoji) == "🌎":
                await umsg.author.send("This is the link for: " + opstat["profile"]["name"] + ".\n" + opstat["profile"]["url"])
                await result.remove_reaction("🌎", umsg.author)
            elif str(reaction.emoji) == "🎲" and operator == None:
                await result.delete()
                await aioop(message, operator)
                return
            elif str(reaction.emoji) == "🗑️":
                await umsg.delete()
                await result.delete()
                return


async def aioskins(message, operator):
    umsg = message
    opname, imglist = await getskins(operator)
    skincount = len(imglist) - 1
    scroll = 0

    embed = discord.Embed(title="Operator Skins")
    embed.set_author(name=opname)
    embed.set_footer(text="Exusiai", icon_url=iconlink)

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "⬅" or "➡" or "🗑️")

    while True:
        embed.set_image(url=imglist[scroll])
        hmsg = await message.channel.send(embed=embed)

        if scroll == 0:
            await hmsg.add_reaction("➡")
            await hmsg.add_reaction("🗑️")
        elif scroll == skincount:
            await hmsg.add_reaction("⬅")
            await hmsg.add_reaction("🗑️")
        else:
            await hmsg.add_reaction("⬅")
            await hmsg.add_reaction("➡")
            await hmsg.add_reaction("🗑️")

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            if not (scroll == 0):
                await hmsg.remove_reaction("⬅", hmsg.author)
            if not (scroll == skincount):
                await hmsg.remove_reaction("➡", hmsg.author)
            await hmsg.remove_reaction("🗑️", hmsg.author)
            return
        else:
            if str(reaction.emoji) == "⬅":
                await hmsg.delete()
                if not (scroll == 0):
                    scroll -= 1
                else:
                    scroll += 1
            elif str(reaction.emoji) == "➡":
                await hmsg.delete()
                if not (scroll == skincount):
                    scroll += 1
                else:
                    scroll -= 1
            elif str(reaction.emoji) == "🗑️":
                await hmsg.delete()
                await umsg.delete()
                return


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
    else:
        cause = "Unknown possible causes"
    embed.add_field(name="Possible Causes", value=cause)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await devreport("op", error)
    await ctx.send(embed=embed)


@bot.command()
async def skins(ctx, *, arg):
    await aioskins(ctx.message, arg)


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
        embed = discord.Embed(title="Command Error!", description="You do not have the permissions to kick anybody!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    except discord.HTTPException:
        embed = discord.Embed(title="Command Error!", description="An error occurred while kicking the player!",
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
        embed = discord.Embed(title="Command Error!", description="You do not have the permissions to ban anybody!",
                              color=discord.Colour.red())
        embed.set_footer(text="Exusiai", icon_url=iconlink)
        await ctx.send(embed=embed)
        return
    except discord.HTTPException:
        embed = discord.Embed(title="Command Error!", description="An error occurred while banning the player!",
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
        embed = discord.Embed(title="Command Error!", description="You do not have the permissions to unban anybody!",
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
    if item == None:
        allitems = ""
        for item in botdb["config"]:
            allitems = allitems + item + ", "
        allitems = stringrip(allitems, ", ")

        await ctx.send("The configs for this bot are: " + allitems)
    else:
        if state.lower() == "true":
            state = True
        else:
            state = False
        botdb["config"][item] = state
        with open("botdb.json", "w") as f:
            json.dump(botdb, f, indent=4)
        
        await ctx.send(item + " is now set to: " + str(state))


@bot.command()
async def rng(ctx, fnum: int = 100, lnum: int = None):
    if lnum == None:
        lnum = fnum
        fnum = 0
    value = random.randrange(fnum, lnum)
    await ctx.send("You got: " + str(value))


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
    if name == None:
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
async def lyric(context, *, name: str = None):
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
    if player == None:
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


@bot.event
async def on_message(message):
    if message.guild:
        if ("https://gamepress.gg/arknights/operator/" in message.content) and botdb["config"]["opparse"]:
            opname = message.content.strip("https://gamepress.gg/arknights/operator").replace("-", " ")
            await aioop(message, opname)

        await bot.process_commands(message)


bot.run(token)
