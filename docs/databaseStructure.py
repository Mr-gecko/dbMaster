import os
import json

TXT_EXT = "txt"
JSON_EXT = "json"

def getDesktop():
    if os.name == "nt":
        return os.environ["HOMEPATH"]+"/Desktop"
    else:
        return os.environ["HOME"]+"/Desktop"

def getExtension(file):
    return file.split(".")[-1]

# TXT FILE
def loadTxt(file):
    with open(file, "r", encoding='utf-8') as f:
        content = f.readlines()
    return content

def writeTxt(file, content:str):
    with open(file, "w") as f:
        f.write(content)
    return content

# JSON FILE
def loadJson(file):
    with open(file, "r") as f:
        content = json.load(f)
    return content

def writeJson(file, content):
    with open(file, "w") as f:
        f.write(content)
    return content

def printJson(content):
    print(json.dumps(content, sort_keys=True, indent=4))

def countTabs(line):
    counter = 0
    for i in range(len(list(line))):
        if list(line)[i] == "\t":
            counter += 1
    return counter

def getValue(line):
    line = cleanLine(line)
    res = line.split(":")[1]
    try:
        if res[0] == " ":
            res = res[1:]
    except:
        pass
    return res

def getKey(line):
    line = cleanLine(line)
    return "".join(line.split(":")[0])

def cleanLine(line):
    line = line.strip("\t")
    line = line.strip("\n")
    return line

def getType(line):
    if countTabs(line) == 0:
        if line == "\n":
            return "empty"
        return "category"
    elif countTabs(line) == 1:
        return "link"
    elif countTabs(line) >= 2:
        return "insight"
    else:
        return "error"


class Database():

    def __init__(self):
        self.data = {}
        self.raw = {}

    def __str__(self):
        return json.dumps(self.data, ensure_ascii=False, sort_keys=True, indent=4)

    def showData(self):
        return Database.pretty(self.data)

    def pretty(data:dict):
        print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))
        return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)

    def retrieve(self, file:str):
        if getExtension(file) == TXT_EXT:
            self.raw = loadTxt(file)
        elif getExtension(file) == JSON_EXT:
            self.raw = loadJson(file)

    def genDict(self):
        tmpData = {}

        for i in range(len(self.raw)):
            if getType(self.raw[i]) == "category":
                currentCategory = getKey(self.raw[i])
                self.data[currentCategory] = []
                currentItemIndex = -1
            elif getType(self.raw[i]) == "link":
                currentItemIndex += 1
                self.data[currentCategory].append({})
                currentItem = cleanLine(self.raw[i])
                self.data[currentCategory][currentItemIndex]["url"] = currentItem
            elif getType(self.raw[i]) == "insight":
                self.data[currentCategory][currentItemIndex][getKey(self.raw[i])] = getValue(self.raw[i])
            elif getType(self.raw[i]) == "error":
                pass
            elif getType(self.raw[i]) == "empty":
                pass

    def get(self, name):
        return self.data[name]

    def sumFloatData(self, dataset:str, key:str):
        res = 0
        for dbi in range(len(self.raw[dataset])):
            for sumIndex in self.raw[dataset][dbi][key]:
                res += float(self.raw[dataset][dbi][key][sumIndex])
        return res

    def sumIntData(self, dataset:str, key:str):
        res = 0
        for dbi in range(len(self.raw[dataset])):
            for sumIndex in self.raw[dataset][dbi][key]:
                res += int(self.raw[dataset][dbi][key][sumIndex])
        return res

    def sumPriceData(self, dataset:str, key:str):
        res = 0
        for dbi in range(len(self.raw[dataset])):
            for sumIndex in self.raw[dataset][dbi][key]:
                number = []
                for char in self.raw[dataset][dbi][key][sumIndex]:
                    if char in list("1234567890,."):
                        number.append(char)
                res += float(number)
        return res


db = Database()
path = "C:\\Users\\vasco\\Documents\\#Dossier\\Acquisti.txt"
db.retrieve(path)
db.genDict()
Database.pretty(db.get("Articoli"))
