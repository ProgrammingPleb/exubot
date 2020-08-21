from datetime import date, datetime, timedelta
from datetime import time as dtime
import time
import asyncio
import aiohttp
import pytz


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://worldtimeapi.org/api/ip") as r:
            otzdata = await r.json()
            ctz = otzdata["timezone"]

    today = date.today()
    ctime = dtime(19, 0, 0)
    resettime = datetime.combine(today, ctime)
    currtime = pytz.timezone(ctz).localize(datetime.now()).astimezone(pytz.timezone("Asia/Kuala_Lumpur"))
    durreset = resettime - currtime
    if durreset.total_seconds() < 0:
        today = date.today() + timedelta(days=1)
        resettime = datetime.combine(today, ctime)
        durreset = resettime - datetime.now()
    rhour = str(int(time.strftime('%H', time.gmtime(durreset.total_seconds()))))
    rmin = str(int(time.strftime('%M', time.gmtime(durreset.total_seconds()))) + 1)
    return rhour, rmin


async def terminal():
    rhour, rmin = await main()
    print("Hours: " + rhour)
    print("Minutes: " + rmin)


if __name__ == "__main__":
    asyncio.run(terminal())
