# This Python file uses the following encoding: utf-8

# Transcript Assembler for Earnings Calls


import sys
import inflect
import re
from bs4 import BeautifulSoup
import collections

flect = inflect.engine()

# truncate float
def truncate(f, n):
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

# is number function
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# Clean points
def cleanPoints(dirtyWord):
    pointEx = "([0-9]+)\.([0-9])"
    if re.search(pointEx, dirtyWord):
        cleanWord = dirtyWord.replace("."," point ")
    else:
        cleanWord = dirtyWord
        
    return cleanWord

# Clean prices
def cleanPrice(dirtyString):
    dirtyStrings = dirtyString.split(" ")
    dollarCentsEx = "\$([0-9]+)\.([0-9])"
    dollarEx = "\$([0-9]+)"
    for i in range(len(dirtyStrings)):
        if re.search(dollarCentsEx, dirtyStrings[i]):
            dirtyStrings[i] = dirtyStrings[i][1:]
            
            # Cents
            if int(dirtyStrings[i].split(".")[0]) == 0:
                dirtyStrings[i] = dirtyStrings[i].split(".")[1] + " cents"
            # Dollars in millions, billions, etc
            elif dirtyStrings[i+1] in ("thousand", "million", "billion", "trillion"):
                dirtyStrings[i+1] = dirtyStrings[i+1] + " dollars"
            # Dollars and cents
            #else:
                #dirtyStrings[i] = dirtyStrings[i].split(".")[0] + " dollars and " + dirtyStrings[i].split(".")[1] + " cents"
        elif re.search(dollarEx, dirtyStrings[i]):
            dirtyStrings[i] = dirtyStrings[i][1:]
            
            if dirtyStrings[i+1] in ("thousand", "million", "billion", "trillion"):
                #dirtyStrings[i] = dirtyStrings[i][1:]
                dirtyStrings[i+1] = dirtyStrings[i+1] + " dollars"
            #else:
                #dirtyStrings[i] = dirtyStrings[i] # + " dollars"
        
    return " ".join(dirtyStrings)
            
# Cleaning function
def clean(dirtyString):
    
    # replace dictionary
    dictSymbols = {
        "%":" percent",
        "-": " ",
        ",": "",
        ";": "",
        "&": "and",
        "'": "",
        "mr.": "mister",
        "mrs.": "misses",
        "ms.": "miss",
    }
    
    # regex replacements
    dirtyString = dirtyString.lower()
    dirtyString = cleanPrice(dirtyString)
    dirtyString = " ".join([cleanPoints(x) for x in dirtyString.split()])
     
    for key, value in dictSymbols.items():
        dirtyString = dirtyString.replace(key, value)
    
    dirtyStrings = dirtyString.split()
   
    #replace digits with words
    for i in range(len(dirtyStrings)):
        if is_number(dirtyStrings[i]):
            dirtyStrings[i] = flect.number_to_words(dirtyStrings[i])
    
    dirtyString = " ".join(dirtyStrings)
    
    # final cleaning
    cleanString = dirtyString.replace('-', ' ')
    
    return cleanString
    
# Get file from argument
try:
    file = sys.argv[1]
except IndexError:
    print("no html file specified")
    exit(1)
    
with open(file, 'r') as f:
    data=f.read()
    
# Get length
try:
    length = sys.argv[2]
except IndexError:
    print("no length specified")
    exit(1)
    
# Create Beautiful Soup Object
soup = BeautifulSoup(data, 'html.parser')

# Initiate variables
speakers = []
transcripts = []
transcriptHolder = ""
speakerHolder = "Start"

# Find paragraph tags within body that contain transcript, save transcript and speaker
for p in soup.find_all('p'):
    if p.find_all('strong'):
        if speakerHolder == "":
            speakerHolder = p.text
        else:
            speakers.append(speakerHolder)
            transcripts.append(transcriptHolder)
            speakerHolder = p.text
            transcriptHolder = ""
    else:
        transcriptHolder = transcriptHolder + " " + p.text

# We don't care about the last iteration since it is the copyright, and we dont care about start, executives, analysts
for i in range(len(speakers)):
    if speakers[i].lower() in ("start", "executives", "analysts", "executive", "analyst"):
        speakers[i] = "delete"
        transcripts[i] = "delete"

speakers = [x for x in speakers if x != "delete"]
transcripts = [x for x in transcripts if x != "delete"]

# Clean transcripts
transcripts = [clean(y) for y in transcripts]

# Get total count of characters
numChars = len("".join(transcripts))

# Get total number of words
numWords = len(" ".join(transcripts).split())

# Get time per character
timePerChar = float(length)/numChars

# Get time per word
timePerWord = float(length)/numWords

# Make dictionary from speakers and transcripts:
transDict = collections.OrderedDict(zip([str(i) + speakers[i].lower().replace(' ','').replace('.','').replace('’','\'') for i in range(len(speakers))], transcripts))

startTime = "0"
endTime = "0"
filename = file.split(".")[0]
outputFile = open(".".join([filename, "stm"]), 'w')
for key, value in transDict.items():
    
    # refactor transcripts to 30 words per line
    transcripts = []
    numPerLine = 30
    numCount = 0
    currentTranscript = ""
    for word in str(value).split():
        if numCount > numPerLine:
            transcripts.append(currentTranscript + word.replace(".",""))
            numCount = 0
            currentTranscript = ""
        else:
            currentTranscript += word.replace(".", "") + " "
            numCount += 1
    
    if currentTranscript != "":
        transcripts.append(currentTranscript[:-1])
    
    for each in transcripts:
        endTime = truncate(float(endTime) + (len(each) * timePerChar + len(each.split()) * timePerWord) / 2, 2)                                #had: file=outputFile
        print(" ".join([filename, str(1), ''.join([i for i in str(key) if not i.isdigit()]), str(startTime), str(endTime), "<o,f0,male>", each]), file=outputFile)
        startTime = endTime
        
outputFile.close()