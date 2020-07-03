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
            async with session.get("https://osu.ppy.sh/api/get_user?k=" + token.strip("\n") + "&u=" + username + "&type=string") as r:
                return (await r.json()), T
    elif type == "best":
        async with aiohttp.ClientSession() as session:
            async with session.get("https://osu.ppy.sh/api/get_user_best?k=" + token.strip("\n") + "&u=" + username + "&type=string") as r:
                bestdata = (await r.json())[0]
        async with aiohttp.ClientSession() as session:
            async with session.get("https://osu.ppy.sh/api/get_beatmaps?k=" + token.strip("\n") + "&b=" + bestdata['beatmap_id']) as r:
                bmapdata = (await r.json())[0]
        return [bestdata, bmapdata]
    elif type == "recent":
        async with aiohttp.ClientSession() as session:
            async with session.get("https://osu.ppy.sh/api/get_user_recent?k=" + token.strip("\n") + "&u=" + username + "&type=string") as r:
                return (await r.json())[0], True
            
            
async def test():
    data = (await main(username="mhikaru117", type="best"))
    print(data)
    print(data[1]['title'])
    print(data[0]['score'])
    print(data[0]['maxcombo'])
    print(data[0]['rank'])
    


if __name__ == "__main__":
    futures = [test()]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(futures))
