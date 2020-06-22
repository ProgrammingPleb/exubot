import sys
import aiohttp
from bs4 import BeautifulSoup
import difflib
import random
import asyncio


async def main(opin=""):
    # Take input and find nearest matching operator
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

    if opin != "":
        opname = difflib.get_close_matches(opin, oplist, 1, 0.5)
    else:
        opname = [random.choice(oplist)]

    # Get the right form for the URL
    opnurl = opname[0].lower().strip("'").strip(" ")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://gamepress.gg/arknights/operator/" + opnurl) as r:
            soup = BeautifulSoup(await r.text(), "lxml")
            for br in soup.find_all("br"):
                br.replace_with("\n")
            opimg = soup.find("div", {"id": "image-tab-1"}).find("a").find("img")
            opurl = "https://gamepress.gg" + opimg["src"].rstrip("\n")
            opinfo = soup.select(".description-box")
            ophp = soup.find("span", {"id": "stat-hp"})
            opatk = soup.find("span", {"id": "stat-atk"})
            opdef = soup.find("span", {"id": "stat-def"})
            opstat = [ophp, opatk, opdef, "https://gamepress.gg/arknights/operator/" + opnurl]

    return opname[0], opurl, opinfo, opstat


async def test():
    try:
        if len(sys.argv) > 1:
            opname, opimg, opinfo, opstat = await main(sys.argv[1])
        else:
            opname, opimg, opinfo, opstat = await main()
    except RuntimeError:
        print("")
    print(opname)
    print(opimg)
    print(opinfo[1].getText())


if __name__ == "__main__":
    asyncio.run(test())
