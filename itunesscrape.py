import urllib.parse
import asyncio
import aiohttp
import json
from datetime import datetime
import time
import lyricsgenius

async def main(name: str = None, media: str = "music"):
    api = "https://itunes.apple.com/search?"

    if media == "music":
        ent = "song"

    if main != None:
        aparams = {"term": name,
                   "country": "US",
                   "media": media,
                   "entity": ent}
        requrl = api + urllib.parse.urlencode(aparams)
        async with aiohttp.ClientSession() as session:
            async with session.get(requrl) as r:
                if r.status == 200:
                    result = json.loads(await r.text())
                    return result, True
                else:
                    return None, False


async def lyrics(name: str = None):
    with open("geniustoken.txt") as f:
        token = f.read()
    
    genius = lyricsgenius.Genius(token)
    genius.verbose = False
    song = genius.search_song(name)
    return song.lyrics


async def test():
    data, status = await main("run joji")
    results = data["results"]
    print(results[0])

    first = results[0]
    tracktime = datetime.fromtimestamp(int(first["trackTimeMillis"])/1000.0)
    trackdur = tracktime - datetime.fromtimestamp(0)
    print(trackdur)
    print(type(trackdur))
    print(trackdur.total_seconds())
    timestamp = time.strftime('%M:%S', time.gmtime(int(trackdur.total_seconds())))
    print(timestamp)

    tracktime = datetime.fromtimestamp(int(first["trackTimeMillis"])/1000.0)
    trackdur = tracktime - datetime.fromtimestamp(0)
    trackhour = time.strftime('%H', time.gmtime(int(trackdur.total_seconds())))

    print(trackhour)
    print(await lyrics("run joji"))


if __name__ == "__main__":
    asyncio.run(test())
    