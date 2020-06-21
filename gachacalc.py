import random
import asyncio


# Gacha Rules
# 3 stars - 40%
# 4 stars - 50%
# 5 stars - 8%
# 6 stars - 2%

async def main():
    # List will need to be updated from time to time
    threestar = ["Fang", "Vanilla", "Plume", "Hibiscus", "Ansel", "Lava", "Steward", "Kroos", "Adnachiel", "Orchid",
                 "Melantha", "Beagle", "Cardigan", "Catapult", "Midnight", "Popukar", "Spot"]
    fourstar = ["Courier", "Scavenger", "Vigna", "Myrrh", "Gavial", "Perfumer", "Haze", "Gitano", "Gravel", "Rope",
                "Shaw", "ShiraYuki", "Meteor", "Jessica", "Deepcolor", "Earthspirit", "Dobermann", "Estelle",
                "Beehunter", "Mousse", "Frostleaf", "Matoimaru", "Cuora", "Gummy", "Matterhorn", "Greyy", "Sussurro",
                "Myrtle", "Dur-nar", "Vermeil", "Ethan", "May", "Ambriel", "Purestream", "Utage", "Conviction",
                "Cutter"]
    fivestar = ["Savage", "Texas", "Ptilopsis", "Silence", "Warfarin", "Amiya", "Nightmare", "Skyfire", "Projekt Red",
                "Manticore", "Cliffheart", "FEater", "Provence", "Blue Poison", "Firewatch", "Meteorite", "Platinum",
                "Pramanix", "Istina", "Mayer", "Sora", "Franka", "Specter", "Indra", "Lappland", "Nearl", "Liskarm",
                "Vulcan", "Croissant", "Grani", "Swire", "Glaucus", "Ceylon", "Astesia", "Flamebringer", "Executor",
                "Breeze", "Waai Fu", "Bison", "Reed", "Broca", "GreyThroat", "Snowsant", "Hung", "Leizi", "Bibeak",
                "Sesa", "Shamare", "Sideroca", "Elysium", "Asbestos", "Tsukinogi"]
    sixstar = ["Ch'en", "Siege", "Shining", "Nightingale", "Ifrit", "Eyjafjalla", "Exusiai", "Angelina",
              "SilverAsh", "Hoshiguma", "Saria", "Skadi", "Schwarz", "Hellagur", "Magallan", "Mostima", "Blaze", "Aak",
              "Nian", "Ceobe", "Bagpipe", "Phantom", "W", "Weedy"]

    # Generate number for Gacha-ing
    opchance = random.randrange(100)
    if opchance <= 40:
        oppull = random.choice(threestar)
        opstar = "3"
    elif opchance <= 90:
        oppull = random.choice(fourstar)
        opstar = "4"
    elif opchance <= 98:
        oppull = random.choice(fivestar)
        opstar = "5"
    else:
        oppull = random.choice(sixstar)
        opstar = "6"
    return oppull, opstar


async def msgsend():
    async def getlist():
        oppull, opstar = await main()
        opmsg = oppull + " (" + opstar + " stars)\n"
        return opmsg
    genlist = [getlist() for _ in range(10)]
    opmsg = await asyncio.gather(*genlist)
    return "".join(opmsg)


async def terminal():
    opchance, opstar = await main()
    print(opchance + " (" + opstar + " stars)")
    opmsg = await msgsend()
    print(opmsg)


if __name__ == "__main__":
    asyncio.run(terminal())
