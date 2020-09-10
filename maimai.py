import sys
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import rpyc


# If no songs are found by a certain name, raise this exception.
class NoSong(Exception):
    def __init__(self, songname):
        self.songname = songname
        self.message = "No songs exist with that name!"
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.songname} -> {self.message}'


# If somehow the Maimai Fandom Site does not return a song URL, raise this one instead.
class NoURL(Exception):
    def __init__(self, songurl):
        self.songurl = songurl
        self.message = "No song URL!"
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.songurl} -> {self.message}'


# Just in case if someone decides not to give a song name at all.
class NoInput(Exception):
    def __init__(self):
        self.message = "No song name was given!"
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.message}'


# This is where we search for the song names based on the search term.
async def mmquery(name=""):
    rlist = {
        "names": [],
        "links": []
    }
    found = False
    
    if name == "":
        raise NoInput

    # Load the Maimai Fandom site and search for the term given.
    async with aiohttp.ClientSession() as session:
        async with session.get("https://maimai.fandom.com/zh/wiki/Special:搜索?query=" + name) as r:         # This is where our search request comes in.
            soup = BeautifulSoup(await r.text(), "lxml")        # Make it readable by the program.
            for br in soup.find_all("br"):
                br.replace_with("\n")       # Change any HTML Line Breaks to Newlines (Discord Friendly)
            qresults = soup.find("ul", {"class": "Results"})        # Get the results returned by the site.
            for result in qresults.find_all("li", {"class": "result"}):     # Then, we find the individual result based on the line above.
                if "樂曲名" in result.find("article").getText():        # Checking if there is "Song Name" in the description of the result.
                    if "歌曲清單" not in result.find("article").getText():      # Some results are categories, which also have "Song Name" in the description, so we exclude those.
                        rlist["names"].append(result.find("a").getText())       # Get the song name...
                        rlist["links"].append(result.find("a")["href"])     # and it's respective fandom link to it.
                        found = True
            if not found:
                raise NoSong(name)      # This is raised if we didn't get any song at all.
    
    return rlist                                                                                            # Then we return a list of songs to be chosen.


# This is where the heavy stuff is, scraping data from both the official song search website, and the Maimai Fandom site as well
async def mminfo(link=""):
    if link == "":
        raise NoURL         # If there is no link when we scraped for the song name and link.
    category = ["POPS & ANIME", "niconico & VOCALOID", "TOUHOU Project", "GAME & VARIETY", "maimai", "ONGEKI & CHUNITHM"]       # Category checks for the song search site.
    catlinks = ["pops_anime", "niconico", "toho", "variety", "maimai", "gekichu"]       # The site link counterpart for the line above.
    diffabb = ["bas", "adv", "exp", "mas", "remas"]     # Difficulty checks.
    data = {
        "jpname": "",
        "enname": "",
        "jpartist": "",
        "enartist": "",
        "category": "",
        "release": "",
        "date": "",
        "diffplatform": "",
        "diffs": [],
        "bpm": "",
        "intl": False,
        "link": link,
        "image": ""
    }       # This is what we'll return once we're finished.

    # Most of the stuff is grabbed from the fandom site.
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as r:
            soup = BeautifulSoup(await r.text(), "lxml")
            for br in soup.find_all("br"):
                br.replace_with("\n")
            details = soup.find_all("table")[1]     # This is where most of the song data is kept.
            data["image"] = details.find("img")["src"]      # Grab the song image.
            for cells in details.find_all("tr"):        # This is the song data we're looking for.
                if "樂曲名" in cells.getText():     # The song's Japanese name. (Used to search in the official site later on)
                    if "(JP)" in cells.getText():
                        for content in cells.find_all("td"):
                            if not content.find("a"):
                                data["jpname"] = content.getText().strip()
                    elif "(EN)" in cells.getText():     # The song's English name. (Shown in International versions of Maimai)
                        for content in cells.find_all("td"):
                            if not content.find("a"):
                                data["enname"] = content.getText().strip()
                    else:
                        for content in cells.find_all("td"):    # Some have not yet been internationally available, so the JP name is just copied over to the EN name.
                            if not content.find("a"):
                                data["jpname"] = content.getText().strip()
                                data["enname"] = content.getText().strip()
                if "演唱/作曲" in cells.getText():      # Artist's Name
                    if "(JP)" in cells.getText():       # In Japanese
                        for content in cells.find_all("td"):
                            if not content.find("a"):
                                data["jpartist"] = content.getText().strip()
                    if "(EN)" in cells.getText():       # In English
                        for content in cells.find_all("td"):
                            if not content.find("a"):
                                data["enartist"] = content.getText().strip()
                    if ("(JP)" and "(EN)") not in cells.getText():      # Just the same situation as the song name if only JP is found.
                        for content in cells.find_all("td"):
                            if not content.find("a"):
                                data["jpartist"] = content.getText().strip()
                                data["enartist"] = content.getText().strip()
                if "類別" in cells.getText():       # Category name(s) for the song
                    i = 0
                    for cell in cells.find_all("th"):
                        if "類別" in cell.getText():
                            data["category"] = cells.find_all("td")[i].getText().strip()
                        i += 1
                if "初出版本" in cells.getText():       # Which platform the song first released on
                    i = 0
                    for cell in cells.find_all("th"):
                        if "初出版本" in cell.getText():
                            data["release"] = cells.find_all("td")[i].getText().strip()
                        i += 1
                if "追加日期" in cells.getText():       # The date that this song was first released (on Maimai)
                    i = 0
                    for cell in cells.find_all("th"):
                        if "追加日期" in cell.getText():
                            newdate = cells.find_all("td")[i].getText().strip().split("/")
                            data["date"] = newdate[2] + "/" + newdate[1] + "/" + newdate[0]
                        i += 1
                if "BPM" in cells.getText():        # Beats per Minute for the song
                    i = 0
                    for cell in cells.find_all("th"):
                        if "BPM" in cell.getText():
                            data["bpm"] = cells.find_all("td")[i].getText().strip()
                        i += 1
    
    # Here is where we do the heavy work,
    # as the official site relies heavily on Javascript,
    # so we have a scraper service running somewhere in the machine to prevent
    # blocking as Discord Bots are asynchronous, thus we cannot have any blocking
    # calls made in our bot.
    i = 0
    for catcheck in category:
        if catcheck in data["category"]:
            scraper = rpyc.connect("localhost", 3333)      # Connect to the scraper service
            agrab = rpyc.async_(scraper.root.dxinfo)        # Wrap the function in an async version of it
            scrape = agrab("https://maimai.sega.com/song/" + catlinks[i] + "/")     # Have it check for the song in the site

            while True:     # Here is where we check if the scraper has finished scraping
                if scrape.ready and not scrape.error:       # If it's done and no errors are made,
                    dxdata = scrape.value       # we grab the data and move on.
                    break
                elif scrape.error:      # Else
                    dxdata = "???"      # We just assume that this is on DX and we couldn't find it
                    data["diffplatform"] = "DX (error)"
                    break

                await asyncio.sleep(0.5)
        i += 1

    found = False
    if dxdata != "???":
        soup = BeautifulSoup(dxdata, "lxml")
        for br in soup.find_all("br"):
            br.replace_with("\n")
        mmresults = soup.find_all("div", {"class": "songs-data-box-music"})     # This is where all the song data lives
        for song in mmresults:
            title = song.find("h2", {"class": "titleText"})     # Get the song name...
            if data["jpname"] in title.getText() and song.find_all("li") != []:     # and see if it matches what we have.
                found = False
                data["diffplatform"] = "DX"     # We confirm that it's on DX...
                data["intl"] = True     # and we confirm that it's on the International Version.
                for diff in diffabb:        # Then we grab all the difficulties of that song (including Re:Master)
                    diffclass = "lev_" + diff
                    diffnum = song.find("li", {"class": diffclass}).getText()
                    if not (diff == "remas" and diffnum == ""):
                        data["diffs"].append(diffnum)
    if not found:       # If we didn't find it on the official site, then we'll just grab it from the fandom site.
        tablecolors = ["170, 232, 186", "249, 230, 170", "240, 187, 202", "201, 169, 203", "220, 206, 221"]     # All the difficulty identifiers
        async with aiohttp.ClientSession() as session:
            async with session.get(data["link"]) as r:
                soup = BeautifulSoup(await r.text(), "lxml")
                for br in soup.find_all("br"):
                    br.replace_with("\n")
                data["diffplatform"] = soup.find_all("table")[2].getText().split(" ")[0].strip()        # This is where the difficulties are at
                for item in soup.find_all("table")[3].find_all("tr"):
                    print(item)
                    for color in tablecolors:
                        search = item.find("td", {"style": "background-color: rgb(" + color + ")"})     # Then we search for the table cell next to the diffculty number
                        if search != [] and search != None:
                            if item.find_all("td")[1].getText().strip() != "":
                                data["diffs"].append(item.find_all("td")[1].getText().strip())      # Then, we just collect it to be returned later on.

    return data     # Once we're done, we just return the data for the song.


# This is the tester, or you can call it the terminal version of the scraper.
async def test():
    if len(sys.argv) > 1:
        output = await mmquery(sys.argv[1])
        print("Songs Found:")
        i = 1
        for song in output["names"]:
            print(str(i) + ". " + song)
            i += 1
        choice = input("Song Number: ")
        print(await mminfo(output["links"][int(choice) - 1]))
    else:
        search = input("Song: ")
        output = await mmquery(search)
        print("Songs Found:")
        i = 1
        for song in output["names"]:
            print(str(i) + ". " + song)
            i += 1
        choice = input("Song Number: ")
        print(await mminfo(output["links"][int(choice) - 1]))


if __name__ == "__main__":
    asyncio.run(test())

