import aiohttp
import asyncio


async def readToken():
    f = open("osutoken.txt")
    token = f.readline()
    f.close()
    return token


async def main(username: str, type: str = "user", mode: str = "std", rank: int = 1):
    token = await readToken()
    
    if type == "user":
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://osu.ppy.sh/api/get_user?k=" + token.strip("\n") + "&u=" + username + "&type=string") as r:
                    if r.status == 200:
                        return (await r.json())[0], True
                    else:
                        return None, False
            except IndexError:
                return None, False
    elif type == "best":
        async with aiohttp.ClientSession() as session:
            async with session.get("https://osu.ppy.sh/api/get_user_best?k=" + token.strip("\n") + "&u=" + username + "&type=string") as r:
                bestdata = (await r.json())[0]
        async with aiohttp.ClientSession() as session:
            async with session.get("https://osu.ppy.sh/api/get_beatmaps?k=" + token.strip("\n") + "&b=" + bestdata['beatmap_id']) as r:
                bmapdata = (await r.json())[0]
        if r.status == 200:
            return [bestdata, bmapdata], True
        else:
            return None, True
    elif type == "recent":
        async with aiohttp.ClientSession() as session:
            async with session.get("https://osu.ppy.sh/api/get_user_recent?k=" + token.strip("\n") + "&u=" + username + "&type=string") as r:
                if r.status == 200:
                    return (await r.json())[0], True
                else:
                    return None, False


async def test():
    data, status = (await main(username="NobodyHasThisUsernameISwear", type="user"))
    print(data)


if __name__ == "__main__":
    asyncio.run(test())
