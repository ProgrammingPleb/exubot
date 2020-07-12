# Python Modules Go Here
import discord
from discord.ext import commands, tasks
import random
import asyncio
import json
import urllib.parse
from datetime import datetime
import time

# Local Modules Go Here
from opscrape import main as opgrab
from servertime import main as rscheck
from gachacalc import msgsend as hhcalc
from skinscrape import main as getskins
from osuscrape import main as osugrab
from animescrape import main as animgrab
from itunesscrape import main as itunes


f = open("token.txt")
token = f.read()
f.close()


f = open("bottype.txt")
bottype = f.read()
f.close()


if bottype.strip("\n") == "release":
    print("Running Release Code....")
    iconlink = "https://img.ezz.moe/0622/17-19-26.png"
    prefix = "e!"
elif bottype.strip("\n") == "testing":
    print("Running Development Code....")
    iconlink = "https://img.ezz.moe/0622/16-15-14.jpg"
    prefix = "t!"
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix))
bot.remove_command('help')


@bot.event
async def on_ready():
    print(f'Exusiai is Online! Client name: {bot.user}')
    if bottype.strip("\n") == "release":
        await bot.change_presence(activity=discord.Game(name=prefix + "help | Exusiai"))
        channel = bot.get_channel(721292304739991552)
        ResetTime(channel=channel)
    else:
        await bot.change_presence(activity=discord.Game(name=prefix + "help | Exusiai (Dev)"))


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


@bot.command()
async def hello(ctx):
    await ctx.send("Yo, Leader!")


@bot.command()
async def help(ctx):
    umsg = ctx.message
    page = 1

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "⬅" or "➡" or "🗑️")

    while True:
        embed = discord.Embed(title="Exusiai Commands")
        embed.set_thumbnail(url=iconlink)
        embed.description = "Locked and loaded, ready for action!\nWhat's the objective today, Leader?\n\n" \
                            "My prefix is " + prefix + "\nSymbols:\n" \
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
                                  "Gives info for the current headhunting banner (EN Server)\n\n"
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
            embed.add_field(name="osu! Commands",
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
                                  "Gives a random number based on the range.")
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
async def materials(ctx):
    await ctx.send("__**Simple EN Farming Table**__ (By Cecaniah Corabelle#8846) :\n"
                   "Link : https://imgur.com/dSS1lIB\n\n"
                   "\*This guide as the name implies is just a simple breakdown of the generally most sanity efficient "
                   "maps, however others do exist depending on the sub-drops you may care about. Please look at "
                   "Penguin Statistics (https://penguin-stats.io/) or this spreadsheet ("
                   "https://docs.google.com/spreadsheets/d/12Jwxr5mJBq73z378Bs-C0e6UcPLp-3UmeuSqAH6XmyQ)")


@bot.command()
async def banner(ctx):
    await ctx.send("The next Standard HeadHunting Banner has been announced featuring higher pull-rates for Siege & "
                   "Saria; which will run from - June 12, 2020, 4:00(UTC-7) to June 26, 2020, 3:59(UTC-7)\n\n"
                   "https://imgur.com/a/NWH3SV6")


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
async def op(ctx, *, arg: str = None):
    umsg = ctx.message
    opname, opimg, opinfo, opstat = await opgrab(arg)
    embed = discord.Embed(title=opname)
    if not (opimg == "???"):
        embed.set_image(url=opimg)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    embed.add_field(name="Operator Description", value=opinfo[1].getText(), inline=False)
    embed.add_field(name="Operator Quote", value=opinfo[2].getText(), inline=False)
    embed.add_field(name="Operator Traits", value=opinfo[0].getText(), inline=False)
    if opstat[0].getText().strip(" ") == "":
        embed.add_field(name="HP", value="???")
    else:
        embed.add_field(name="HP", value=opstat[0].getText())
    if opstat[1].getText().strip(" ") == "":
        embed.add_field(name="ATK", value="???")
    else:
        embed.add_field(name="ATK", value=opstat[1].getText())
    if opstat[2].getText().strip(" ") == "":
        embed.add_field(name="DEF", value="???")
    else:
        embed.add_field(name="DEF", value=opstat[2].getText())
    if arg == None:
        msgopt = "🌎 to get the link to operator's info\n" \
                 "👕 to get the operator's skins\n" \
                 "🎲 to re-roll for another operator\n" \
                 "🗑️ to remove this message"
    else:
        msgopt = "🌎 to get the link to operator's info\n" \
                 "👕 to get the operator's skins\n" \
                 "🗑️ to remove this message"
    embed.add_field(name="Actions", value=msgopt, inline=False)
    print(type(opinfo[1].getText()))
    result = await ctx.send(embed=embed)

    await result.add_reaction("🌎")
    await result.add_reaction("👕")
    if arg == None:
        await result.add_reaction("🎲")
    await result.add_reaction("🗑️")

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "🌎" or "👕" or "🎲" or "🗑️")

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await result.remove_reaction("🌎", result.author)
            await result.remove_reaction("👕", result.author)
            await result.remove_reaction("🎲", result.author)
            await result.remove_reaction("🗑️", result.author)
            return
        else:
            if str(reaction.emoji) == "🌎":
                await umsg.author.send("This is the link for: " + opname + ".\n" + opstat[3])
                await result.remove_reaction("🌎", umsg.author)
            elif str(reaction.emoji) == "👕":
                await result.delete()
                await skins(ctx, arg=opname)
                return
            elif str(reaction.emoji) == "🎲" and arg == None:
                await result.delete()
                await op(ctx)
                return
            elif str(reaction.emoji) == "🗑️":
                await umsg.delete()
                await result.delete()
                return


@bot.command()
async def skins(ctx, *, arg):
    umsg = ctx.message
    opname, imglist = await getskins(arg)
    skincount = len(imglist) - 1
    scroll = 0

    embed = discord.Embed(title="Operator Skins")
    embed.set_author(name=opname)
    embed.set_footer(text="Exusiai", icon_url=iconlink)

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "⬅" or "➡" or "🗑️")

    while True:
        embed.set_image(url=imglist[scroll])
        hmsg = await ctx.send(embed=embed)

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
    opname, opimg, opinfo, opstat = await opgrab(random.choice(awaifu))
    embed = discord.Embed(title="Waifu Headhunt")
    embed.description = "You got: **" + opname + "**!"
    embed.set_image(url=opimg)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    await ctx.send(embed=embed)


@bot.command()
async def husbando(ctx):
    ahusbando = ["12F", "Bison", "Castle-3", "Courier", "Greyy", "Hellagur", "Matterhorn", "Midnight", "Noir Corne",
                 "Ranger", "Steward", "SliverAsh", "Spot"]
    opname, opimg, opinfo, opstat = await opgrab(random.choice(ahusbando))
    embed = discord.Embed(title="Husbando Headhunt")
    embed.description = "You got: **" + opname + "**!"
    embed.set_image(url=opimg)
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
    umsg = ctx.message.id
    if name == None:
        embed = discord.Embed(title="Error!", description="No anime title was given!",
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

bot.run(token)
