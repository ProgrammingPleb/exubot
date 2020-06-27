import discord
from discord.ext import commands, tasks
from opscrape import main as opgrab
from servertime import main as rscheck
from gachacalc import msgsend as hhcalc
from skinscrape import main as getskins
import random
import asyncio

f = open("token.txt")
token = f.readline()
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
async def ccrisk(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/586588958885150721/708704147591004220/FB_IMG_1589016478287"
                   ".jpg")


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
async def op(ctx, *, arg):
    umsg = ctx.message
    opname, opimg, opinfo, opstat = await opgrab(arg)
    embed = discord.Embed(title=opname)
    embed.set_image(url=opimg)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    embed.add_field(name="Operator Description", value=opinfo[1].getText(), inline=False)
    embed.add_field(name="Operator Quote", value=opinfo[2].getText(), inline=False)
    embed.add_field(name="Operator Traits", value=opinfo[0].getText(), inline=False)
    embed.add_field(name="HP", value=opstat[0].getText())
    embed.add_field(name="ATK", value=opstat[1].getText())
    embed.add_field(name="DEF", value=opstat[2].getText())
    embed.add_field(name="Actions", value="🌎 to get the link to operator's info\n"
                                          "👕 to get the operator's skins\n"
                                          "🗑️ to remove this message", inline=False)
    print(type(opinfo[1].getText()))
    result = await ctx.send(embed=embed)

    await result.add_reaction("🌎")
    await result.add_reaction("👕")
    await result.add_reaction("🗑️")

    def check(reaction, user):
        return user == umsg.author and (str(reaction.emoji) == "🌎" or "👕" or "🗑️")

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await result.remove_reaction("🌎", result.author)
            await result.remove_reaction("👕", result.author)
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
            elif str(reaction.emoji) == "🗑️":
                await umsg.delete()
                await result.delete()
                return


@op.error
async def op_error(ctx, error):
    umsg = ctx.message
    opname, opimg, opinfo, opstat = await opgrab()
    embed = discord.Embed(title=opname)
    embed.set_image(url=opimg)
    embed.set_footer(text="Exusiai", icon_url=iconlink)
    embed.add_field(name="Operator Description", value=opinfo[1].getText(), inline=False)
    embed.add_field(name="Operator Quote", value=opinfo[2].getText(), inline=False)
    embed.add_field(name="Operator Traits", value=opinfo[0].getText(), inline=False)
    embed.add_field(name="HP", value=opstat[0].getText())
    embed.add_field(name="ATK", value=opstat[1].getText())
    embed.add_field(name="DEF", value=opstat[2].getText())
    embed.add_field(name="Actions", value="🌎 to get the link to operator's info\n"
                                          "👕 to get the operator's skins\n"
                                          "🎲 to re-roll for another operator\n"
                                          "🗑️ to remove this message", inline=False)
    print(opimg)
    result = await ctx.send(embed=embed)

    await result.add_reaction("🌎")
    await result.add_reaction("👕")
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
            elif str(reaction.emoji) == "🎲":
                await result.delete()
                await op_error(ctx, error)
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
    uid = int(player.replace("<@!", "").replace(">", ""))

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
    uid = int(player.replace("<@!", "").replace(">", ""))

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
    uid = int(player.replace("<@!", "").replace(">", ""))

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


bot.run(token)
