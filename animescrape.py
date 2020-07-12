from jikanpy import AioJikan
import asyncio


async def main(anime: str):
    async with AioJikan() as mal:
        query = await mal.search('anime', anime, page=1)
    
    return query["results"]


async def test():
    print(type(await main("boku no hero")))
    data = (await main("boku no hero 1"))
    print(type(data[0]))
    print(data[0])

if __name__ == "__main__":
    asyncio.run(test())
