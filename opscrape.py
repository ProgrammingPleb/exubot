import sys
import aiohttp
from bs4 import BeautifulSoup
import difflib
import random
import asyncio
import re
import urllib


class NoOperator(Exception):
    def __init__(self, opname):
        self.opname = opname
        self.message = "No operators exist with that name!"
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.opname} -> {self.message}'


class CNOperator(Exception):
    def __init__(self, opname):
        self.opname = opname
        self.message = "This operator still has not enough info!"
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.opname} -> {self.message}'


async def main(opin = None):
    # Take input and find nearest matching operator
    # Deprecated due to maintainability issues
    """
    oplist = ["Rosa (Poca)", "Leonhardt", "Absinthe", "Podenco", "Tsukinogi", "Asbestos", "Weedy", "W", "Elysium",
              "Thermal-EX", "Phantom", "Shamare", "Sideroca", "Cutter", "Conviction", "Bagpipe", "Sesa", "Bibeak",
              "Utage", "Purestream", "Ceobe", "Leizi", "Nian", "Aak", "Hung", "Snowsant", "Blaze", "GreyThroat",
              "Ambriel", "Broca", "Reed", "Mostima", "Bison", "Waai Fu", "May", "Ceylon", "Flamebringer", "Breeze",
              "Ethan", "Dur-nar", "Magallan", "Vermeil", "Executor", "Hellagur", "Myrtle", "Astesia", "Schwarz",
              "Greyy", "Sussurro", "Swire", "Glaucus", "Ch'en", "Popukar", "Spot", "Skadi", "Grani", "Nightmare",
              "Beehunter", "Midnight", "Catapult", "Savage", "SilverAsh", "Saria", "Hoshiguma", "Nightingale",
              "Shining", "Angelina", "Eyjafjalla", "Ifrit", "Siege", "Exusiai", "FEater", "Manticore", "Sora", "Istina",
              "Pramanix", "Cliffheart", "Firewatch", "Provence", "Vulcan", "Croissant", "Liskarm", "Projekt Red",
              "Nearl", "Warfarin", "Silence", "Mayer", "Skyfire", "Amiya", "Meteorite", "Platinum", "Blue Poison",
              "Specter", "Lappland", "Indra", "Franka", "Texas", "Zima", "Ptilopsis", "Shaw", "Earthspirit",
              "Deepcolor", "Gummy", "Cuora", "Matterhorn", "Perfumer", "Gavial", "Myrrh", "Rope", "Gravel", "Mousse",
              "Estelle", "Frostleaf", "Matoimaru", "Dobermann", "Vigna", "Scavenger", "Courier", "Shirayuki", "Meteor",
              "Jessica", "Gitano", "Haze", "Orchid", "Steward", "Ansel", "Hibiscus", "Lava", "Adnachiel", "Kroos",
              "Beagle", "Cardigan", "Melantha", "Plume", "Vanilla", "Fang", "12F", "Durin", "Rangers", "Noir Corne",
              "Yato", "Castle-3", "Lancet-2"]

    if opin != None:
        opname = difflib.get_close_matches(opin, oplist, 1, 0.5)
    else:
        opname = [random.choice(oplist)]
    """

    # Search the Arknights Fandom Wiki for nearest operator match
    # Yes, I'm relying on other services to do the work for me.
    if opin != None:
        searchdata = opin
        oparticle = None
        opfound = False
        opquery = urllib.parse.quote(opin, safe="")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://mrfz.fandom.com/wiki/Special:Search?query=" + opquery) as r:
                soup = BeautifulSoup(await r.text(), "lxml")
                for br in soup.find_all("br"):
                    br.replace_with("\n")
                qresult = soup.find("ul", {"class": "Results"})
                if qresult is None:
                    raise NoOperator(opin)
                for article in qresult.find_all("article"):
                    if "/File" in article.getText() and not opfound:
                        opname = article("a")[0].getText().replace("/File", "")
                        opfound = True
                    if "/Stats" in article.getText() and not opfound:
                        opname = article("a")[0].getText().replace("/Stats", "")
                        opfound = True
                    elif "(CN" in article.getText() and not opfound:
                        opname = article("a")[0].getText()
                        raise CNOperator(opname)
                if not opfound:
                    raise NoOperator(opin)
    else:
        opstar = random.randrange(4,7)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://mrfz.fandom.com/wiki/Special:RandomInCategory/" + str(opstar) + "-star") as r:
                soup = BeautifulSoup(await r.text(), "lxml")
                opname = soup.find("h1", {"class": "page-header__title"}).getText()
                searchdata = opname


    # Get the right form for the URL
    opnurla = opname.lower().replace("'", "").replace(" ", "-")
    opnurlf = opname.replace("'", "%27").replace(" ", "_")


    # Deprecated due to GamePress changes
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://gamepress.gg/arknights/operator/" + opnurl) as r:
            soup = BeautifulSoup(await r.text(), "lxml")
            for br in soup.find_all("br"):
                br.replace_with("\n")
            try:
                opimg = soup.find("div", {"id": "image-tab-1"}).find("a").find("img")
                opurl = "https://gamepress.gg" + opimg["src"].rstrip("\n")
            except AttributeError:
                opimg = "???"
                opurl = "Link Not Found"
            opinfo = soup.select(".description-box")
            ophp = soup.find("div", {"id": "stat-hp"})
            if ophp == None:
                ophp = ""
            opatk = soup.find("span", {"id": "stat-atk"})
            if opatk == None:
                opatk = ""
            opdef = soup.find("span", {"id": "stat-def"})
            if opdef == None:
                opdef = ""
            opstat = [ophp, opatk, opdef, "https://gamepress.gg/arknights/operator/" + opnurl]
    """


    # Define Base Data
    opstat = {
        "profile": {
            "name": "",
            "artist": "",
            "cv": "",
            "gender": "",
            "PoB": "",
            "bday": "",
            "race": "",
            "height": "",
            "archetype": "",
            "cbex": "",
            "physstg": "",
            "mobile": "",
            "physend": "",
            "tactic": "",
            "cbskill": "",
            "originium": "",
            "quote": "",
            "desc": "",
            "fulldesc": "",
            "tags": [],
            "traits": "",
            "url": "",
            "imgurl": ""
        }, "stats": {
            "e2": True,
            "s1": {
                "HP": 0, "ATK": 0, "DEF": 0, "RES": 0, "RDP": 0, "DP": 0, "Block": 0, "ASPD": 0.0
            }, "s2": {
                "HP": 0, "ATK": 0, "DEF": 0, "RES": 0, "RDP": 0, "DP": 0, "Block": 0, "ASPD": 0.0
            }, "s3":{
                "HP": 0, "ATK": 0, "DEF": 0, "RES": 0, "RDP": 0, "DP": 0, "Block": 0, "ASPD": 0.0
            }, "s4": {
                "HP": 0, "ATK": 0, "DEF": 0, "RES": 0, "RDP": 0, "DP": 0, "Block": 0, "ASPD": 0.0
            }
        }, "search": searchdata
    }

    opstat["profile"]["name"] = opname
    opstat["profile"]["url"] = "https://gamepress.gg/arknights/operator/" + opnurla

    # GamePress will still be used, only for certain static data
    async with aiohttp.ClientSession() as session:
        async with session.get("https://gamepress.gg/arknights/operator/" + opnurla) as r:
            soup = BeautifulSoup(await r.text(), "lxml")
            for br in soup.find_all("br"):
                br.replace_with("\n")

            try:
                opstat["profile"]["imgurl"] = "https://gamepress.gg" + soup.find("div", {"id": "image-tab-1"}).find("a").find("img")["src"]
            except AttributeError:
                opstat["profile"]["imgurl"] = "???"
            
            profdiv = soup.find("div", {"class": "profile-info-table"})
            proftables = profdiv("table")
            proft1 = ["gender", "PoB", "bday", "race", "height", "cbex"]
            i = 0
            for item in proftables[1]("td"):
                opstat["profile"][proft1[i]] = (item.getText().strip("\n").strip(" "))
                i += 1
            proft2 = ["physstg", "mobile", "physend", "tactic", "cbskill", "originium"]
            i = 0
            for item in proftables[2]("td"):
                opstat["profile"][proft2[i]] = (item.getText().strip("\n").strip(" "))
                i += 1

            opqdt = ["traits", "desc", "quote"]
            i = 0
            for item in soup.find_all("div", {"class": "description-box"}):
                opstat["profile"][opqdt[i]] = item.getText().strip()
                i += 1
            
            opstat["profile"]["fulldesc"] = soup.find("div", {"class": "profile-description"}).getText()
            for tag in soup.find_all("div", {"class": "tag-cell"})[0].find_all("a"):
                opstat["profile"]["tags"].append(tag.getText().strip("\n"))
            try:
                opstat["profile"]["archetype"] = soup.find_all("div", {"class": "tag-cell"})[1].find("a").getText().strip("\n")
            except IndexError:
                opstat["profile"]["archetype"] = "N/A"


    # We're now grabbing the data from the Arknights Fandom Wiki, since
    # the data given there is static, in a form of a table.
    # Will change if we find any website with an interactable form on
    # the stats page
    async with aiohttp.ClientSession() as session:
        async with session.get("https://mrfz.fandom.com/wiki/" + opnurlf + "/Stats") as r:
            soup = BeautifulSoup(await r.text(), "lxml")
            for br in soup.find_all("br"):
                br.replace_with("\n")
            
            table = soup('td', limit=40)
            tdata = []
            i = 1
            offset = 0
            if table[3].getText() == " ":
                offset = -1
                opstat["stats"]["e2"] = False
            for item in table:
                try:
                    if i < 5 + offset:
                        opstat["stats"]["s" + str(i)]["HP"] = int(item.getText())
                    elif i > 5 and i < 10 + offset:
                        opstat["stats"]["s" + str(i - 5)]["ATK"] = int(item.getText())
                    elif i > 10 and i < 15 + offset:
                        opstat["stats"]["s" + str(i - 10)]["DEF"] = int(item.getText())
                    elif i > 15 and i < 20 + offset:
                        opstat["stats"]["s" + str(i - 15)]["RES"] = int(item.getText())
                    elif i > 20 and i < 25 + offset:
                        opstat["stats"]["s" + str(i - 20)]["RDP"] = int(item.getText())
                    elif i > 25 and i < 30 + offset:
                        opstat["stats"]["s" + str(i - 25)]["DP"] = int(item.getText())
                    elif i > 30 and i < 35 + offset:
                        opstat["stats"]["s" + str(i - 30)]["Block"] = int(item.getText())
                    elif i > 35 and i < 40 + offset:
                        opstat["stats"]["s" + str(i - 35)]["ASPD"] = float(item.getText())
                except ValueError:
                    if i < 5 + offset:
                        opstat["stats"]["s" + str(i)]["HP"] = "???"
                    elif i > 5 and i < 10 + offset:
                        opstat["stats"]["s" + str(i - 5)]["ATK"] = "???"
                    elif i > 10 and i < 15 + offset:
                        opstat["stats"]["s" + str(i - 10)]["DEF"] = "???"
                    elif i > 15 and i < 20 + offset:
                        opstat["stats"]["s" + str(i - 15)]["RES"] = "???"
                    elif i > 20 and i < 25 + offset:
                        opstat["stats"]["s" + str(i - 20)]["RDP"] = "???"
                    elif i > 25 and i < 30 + offset:
                        opstat["stats"]["s" + str(i - 25)]["DP"] = "???"
                    elif i > 30 and i < 35 + offset:
                        opstat["stats"]["s" + str(i - 30)]["Block"] = "???"
                    elif i > 35 and i < 40 + offset:
                        opstat["stats"]["s" + str(i - 35)]["ASPD"] = "???"
                    i += 1
                i += 1


    # We're getting the artist and CV here due to Cloudflare Email Obfuscation messing around
    # with some artist names i.e. artist for Blaze which has an @ sign     
    async with aiohttp.ClientSession() as session:
        async with session.get("https://mrfz.fandom.com/wiki/" + opnurlf + "/File") as r:
            if r.status == 200:
                soup = BeautifulSoup(await r.text(), "lxml")
                opstat["profile"]["artist"] = soup.find("div", {"data-source": "illustrator"}).find("div").getText()
                opstat["profile"]["cv"] = soup.find("div", {"data-source": "cv"}).find("div").getText()
            else:
                async with session.get("https://gamepress.gg/arknights/operator/" + opnurla) as rfall:
                    soupfall = BeautifulSoup(await rfall.text(), "lxml")
                    i = 0
                    profdiv = soupfall.find("div", {"class": "profile-info-table"})
                    proftables = profdiv("table")
                    proft0 = ["artist", "cv"]
                    for item in proftables[0]("td"):
                        opstat["profile"][proft0[i]] = (item.getText().strip("\n").strip(" "))
                        i += 1

    return opstat


async def test():
    received = await main("poca")
    print(received)
    # await main("blaze")


if __name__ == "__main__":
    asyncio.run(test())
