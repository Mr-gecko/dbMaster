import os
import eyed3
import datetime
import json
import time

eyed3.log.setLevel("ERROR")


print("\033[?25l") # hide cursor

def saveData(file:str, data:dict):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"data saved to {file}")

def loadData(file:str):
    with open(file, "r", encoding='utf-8') as f:
        data = json.load(f)
    return data

def saveShow(file:str, show:str):
    with open(file, "w", encoding='utf-8') as f:
        f.write(show)
    print(f"data saved to {file}")

def bar(prog, total, show:str=""):
    scale = 50
    per = (prog/float(total))*scale
    b = "█" * int(per) + "-" * (scale-int(per))
    print(f"\r |{b}| {int(100*(per/scale))}/100% - {show}", end="\r")

def lastUpdated():
    return f"LAST UPDATED: {datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")}"

def whenAdded():
    return f"ADDED: {datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")}"

def addedPrev():
    return f"ADDED PREVIOUS: {datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S")}"

def maxLen(lines:list):
    max = 0
    for line in lines:
        if len(line)>max:
            max = len(line)
    return max

def spaceMax(x1:str, x2:str, max:int, separator:str="   "):
    global SEPARATOR
    res = f"{x1}{' '*(max-len(x1))}{separator}{x2}"
    return res

def cutName(name:str, x:int):
    res = name[:x]+"..."
    res = res + " "*(x-(len(res)-1)+3)
    return res

def getExtension(file:str):
    return file.split(".")[-1]

def formatTime(seconds:int, days:bool=False):
    sec = seconds
    min, sec = divmod(sec, 60)
    hou, min = divmod(min, 60)
    if days:
        day, hou = divmod(hou, 24)
        time = f"{int(day):01d}:{int(hou):02d}:{int(min):02d}:{int(sec):02d}"
    else:
        time = f"{int(hou):02d}:{int(min):02d}:{int(sec):02d}"
    return time

def unformatTime(time:str):
    items = time.split(":")
    hou = int(items[0])
    min = int(items[1])
    sec = int(items[2])
    min += (hou*60)
    sec += (min*60)
    return int(sec)

def gatherInfo(data:dict):
    numberOfAlbums = 0
    numberOfSongs = 0
    totalListenTime = 0
    albumArtistsList = []
    allArtistsList = []
    genresList = []
    albumsList = []
    songsList = []

    for album in data:
        if album == "info":
            continue
        numberOfAlbums += 1
        albumsList.append(album)
        albumArtistsList.append(data[album]["artist"])
        totalListenTime += unformatTime(data[album]["duration"])
        for song in data[album]["songs"]:
            numberOfSongs += 1
            songsList.append(song["title"])
            for artist in song["artists"]:
                if not artist in allArtistsList:
                    allArtistsList.append(artist)
            if not song["genre"] in genresList:
                genresList.append(song["genre"])
    info = {
        "numberOfAlbums":numberOfAlbums,
        "numberOfSongs":numberOfSongs,
        "albumArtistsList":albumArtistsList,
        "allArtistsList":allArtistsList,
        "genresList":genresList,
        "totalListenTime":formatTime(totalListenTime, days=False),
        "albumsList":albumsList,
        "songsList":songsList
    }

    return info

def printInfo(info:dict):
    print(f"""\

Songs List:  \n\t{'\n\t'.join([song for song in info['songsList']])}

Albums List:  \n\t{'\n\t'.join([album for album in info['albumsList']])}

Genres List:  \n\t{'\n\t'.join([genre for genre in info['genresList']])}

Album Artists:  \n\t{'\n\t'.join([artist for artist in info['albumArtistsList']])}

All Artists:  \n\t{'\n\t'.join([artist for artist in info['allArtistsList']])}

Total Albums: {info['numberOfAlbums']}
Total Songs:  {info['numberOfSongs']}
Total Listen Time:  {info['totalListenTime']}
""")

def getMusic(prev:bool=False):
    data = {
        "info": lastUpdated()
    }
    albums = {}
    folder = input("folder: ")
    os.chdir(folder)
    total = 0
    prog = 0
    for alb in os.listdir(folder):
        if os.path.isdir(alb):
            if alb == "System Volume Information":
                continue
            total += len(os.listdir(alb))
    for album in os.listdir(folder):
        if not os.path.isdir(album) or album == "System Volume Information":
            continue
        # print(f"reading {album}")
        albums[album] = {
            "artist":"",
            "year": "",
            "genre":"",
            "duration":"",
            "info": whenAdded() if not prev else addedPrev(),
            "songs":[]
        }
        albumDuration = 0
        for file in os.listdir(album):
            # print(f"reading   {file}")
            prog += 1
            bar(prog, total, cutName(file.split(".")[0], 35))  # SONG SHOWER
            #bar(prog, total, cutName(album, 25))  # ALBUM SHOWER
            if file.split(".")[-1] == "mp3":
                audioFile = eyed3.load(album+"/"+file)
                albumDuration += audioFile.info.time_secs
                duration = formatTime(audioFile.info.time_secs)
                audioFile = audioFile.tag
                albumArtist = audioFile.album_artist
                albums[album]["songs"].append({
                    "title": str(audioFile.title) if audioFile.title != None else "no Title",
                    "artists": audioFile.artist.split(", ") if audioFile.artist != None else "no Artists",
                    "year":str(audioFile.recording_date) if audioFile.recording_date != None else "no Year",
                    "genre":str(audioFile.genre.name) if audioFile.genre.name != None else "no Genre",
                    "duration":str(duration),
                    "source url":str(audioFile.audio_file_url) if audio_file_url != None else "no Url"
                })

        albums[album]["artist"] = "Various Artists" if albumArtist == None else albumArtist
        albums[album]["year"] = str(audioFile.recording_date) if audioFile.recording_date != None else "no Year"
        albums[album]["genre"] = str(audioFile.genre.name) if audioFile.genre.name != None else "no Genre"
        albums[album]["duration"] = str(formatTime(albumDuration))

    data = dict(data, **albums)

    # print(json.dumps(data, indent=2, ensure_ascii=False))
    print() # to exit the loading bar
    return data

def addMusic(oldData:dict, prev:bool=False):
    # data = {
    #     "info": lastUpdated()
    # }
    data = {}
    albums = {}
    folder = input("folder: ")
    os.chdir(folder)
    total = 0
    prog = 0
    for alb in os.listdir(folder):
        if os.path.isdir(alb):
            if alb == "System Volume Information":
                continue
            total += len(os.listdir(alb))
    for album in os.listdir(folder):
        if not os.path.isdir(album) or album == "System Volume Information":
            continue
        # print(f"reading {album}")
        albums[album] = {
            "artist":"",
            "year": "",
            "genre":"",
            "duration":"",
            "info": whenAdded() if not prev else addedPrev(),
            "songs":[]
        }
        albumDuration = 0
        for file in os.listdir(album):
            # print(f"reading   {file}")
            prog += 1
            bar(prog, total, cutName(file.split(".")[0], 35))  # SONG SHOWER
            #bar(prog, total, cutName(album, 25))  # ALBUM SHOWER
            if file.split(".")[-1] == "mp3":
                audioFile = eyed3.load(album+"/"+file)
                albumDuration += audioFile.info.time_secs
                duration = formatTime(audioFile.info.time_secs)
                audioFile = audioFile.tag # THIS IS BECAUSE info.time_secs DON'T NEED .tag FIRST
                albumArtist = audioFile.album_artist
                albums[album]["songs"].append({
                    "title": str(audioFile.title) if audioFile.title != None else "no Title",
                    "artists": audioFile.artist.split(", ") if audioFile.artist != None else "no Artists",
                    "year":str(audioFile.recording_date) if audioFile.recording_date != None else "no Year",
                    "genre":str(audioFile.genre.name) if audioFile.genre.name != None else "no Genre",
                    "duration":str(duration),
                    "source url":str(audioFile.audio_file_url) if audio_file_url != None else "no Url"
                })

        albums[album]["artist"] = "Various Artists" if albumArtist == None else albumArtist
        albums[album]["year"] = str(audioFile.recording_date) if audioFile.recording_date != None else "no Year"
        albums[album]["genre"] = str(audioFile.genre.name) if audioFile.genre.name != None else "no Genre"
        albums[album]["duration"] = str(formatTime(albumDuration))

    data = dict(data, **albums)
    data  = dict(oldData, **data)
    data["info"] = lastUpdated()

    # print(json.dumps(data, indent=2, ensure_ascii=False))
    print() # to exit the loading bar
    return data

def show(data:dict, artist:bool=True, year:bool=True, genre:bool=True, info:bool=True, duration:bool=True,titles:bool=True, artists:bool=True):
    gathered = gatherInfo(data)
    lines  = []
    ALBUM_ART = ""
    ALBUM_SEPARATOR = ", "
    SONG_SEPARATOR = " - "
    SONG_APPENDIX = "|"
    MAXLEN = 70
    SONG_BASE_LINE = f"{' '*len(ALBUM_ART)}\t"
    for album in data:
        if album == "info":
            lines.append(data[album])
            lines.append(f"Number of Albums: {gathered['numberOfAlbums']}")
            lines.append(f"Number of Songs:  {gathered['numberOfSongs']}")
            lines.append(f"Total Duration:   {gathered['totalListenTime']}")
            continue
        else:
            line = f"\n{ALBUM_ART}{album}"  # \n to leave a line between each album, for better reading, AND ALBUM_ART IS CUSTOM
            album_base_line = line
            if artist:
                line = line + ALBUM_SEPARATOR + data[album]["artist"]
            if year:
                line = line + ALBUM_SEPARATOR + data[album]["year"]
            if genre:
                line = line + ALBUM_SEPARATOR + data[album]["genre"]
            if duration:
                line = line + ALBUM_SEPARATOR + "duration: " + data[album]["duration"]
            if info:
                line = line + ALBUM_SEPARATOR + data[album]["info"]
            lines.append(line)
            for song in data[album]["songs"]:
                line = SONG_BASE_LINE   # TO INDENT INSIDE THE ALBUM, OPTIONAL BUT PREFFERED FOR BETTER READING
                if titles:
                    line = line + SONG_APPENDIX + song["title"]
                if artists:
                    if titles:  # NEED TO ADD A SEPARATOR, BECAUSE LINE IS NOT EMPTY
                        line = SONG_BASE_LINE
                        line = line + SONG_APPENDIX + spaceMax(song["title"], ", ".join(song["artists"]), max=MAXLEN, separator=SONG_APPENDIX) # ", " is changable, maybe in the future
                                                    # SONG APPENDIX IS JUST FOR GRAPHICS, OPTIONAL
                    else:   # LINE IS EMPTY SO NO NEED TO ADD SEPARATOR
                        line = line + SONG_APPENDIX + ", ".join(song["artists"])
                if line == SONG_BASE_LINE:
                    pass
                else:
                    lines.append(line)



    res = "\n".join(lines)
    return res


# data = loadData(f"{path}\\musicData.json")
# data = addMusic(data, prev=True)
# saveData(f"{path}\\musicDataUpdated.json", data)

dataPath = "C:\\Users\\vasco\\Desktop\\musicData.json"
showPath = "C:\\Users\\vasco\\Desktop\\music.txt"

print("""\
Options:
(1) create db
(2) add music to db
(3) convert music db to text
(4) gather info from db
""")
cmd = str(input("option: "))
if cmd == "1":
    data = getMusic(prev=False)
    saveData(dataPath, data)
    saveShow(showPath, show(data))
elif cmd == "2":
    oldData = loadData(str(input("db file: ")))
    data = addMusic(oldData, prev=False)
    saveData(dataPath, data)
    saveShow(showPath, show(data))
elif cmd == "3":
    data = loadData(str(input("db file: ")))
    text = show(data)
    print(text)
    saveShow(showPath, text)
elif cmd == "4":
    data = loadData(str(input("db file: ")))
    info = gatherInfo(data)
    printInfo(info)

# data = getMusic(prev=True)
# saveData("C:\\Users\\vasco\\Desktop\\musicData.json", data)
# saveShow("C:\\Users\\vasco\\Desktop\\music.txt", show(data))
