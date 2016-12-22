#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import glob
import subprocess
import natsort
import shutil


#                    Generate text lines based on chopped transcript audio files.
#                     ** using timeEnd to provide ~50s worth of lines above and below

# for each chopped audio file, estimate the time-corresponding line of text and a previous/following line or more

#  using: chopped audio file directory created by chop_wav_silence



# make chopped_text_file dir if not there
if not os.path.isdir("chopped_text_file"):
    os.makedirs("chopped_text_file")
    


# read in the text transcript, stm file  vv

fileText = open('BPearnCall.stm','r')

textLinesFull = fileText.readlines()

fileText.close()           # CME call -- 314 lines total


#lists of only start,stop times
textStart = []
textStop = []

for line in textLinesFull:
    workingLine = line.split("<")[0].split(" ")    # split by spaces after getting first part of line
    workingLine = workingLine[3:5]
    
    textStart.append(workingLine[0])
    textStop.append(workingLine[1])
    
    


# list of only spoken text
onlyText = []

for line in textLinesFull:
    workingLine = line.split("> ")[1]
    
    onlyText.append(workingLine)
    



# list of wav files
#wavList = glob.glob("chopped_audio_file/*")      # file names saved as chopped_audio/CME2016....

if not os.path.isdir("chopped_audio_file"):
    print("Required directory 'chopped_audio_file' not found")
else:
    #wavList = os.listdir("chopped_audio_file/")
    wavList = glob.glob("chopped_audio_file/*.wav")  #only wav files
    for j in range(len(wavList)): wavList[j]=wavList[j].replace("chopped_audio_file/","")
    
    if wavList[0][0:3]== ".DS":
        del wavList[0]      # delete .DS_Store.  
               #Note files not alphabetically ordered. text files are then not written in order


    

# find the time point of line with "[operator instructions]".  text b4 here is "covered faster" by speakers. and afterward, is covered slower in the QA session
for i in range(2,len(onlyText)):     # skip line1 and2 (index0, 1)
    if "[operator" in onlyText[i]:
        timeOfOperator = textStop[i]      #gets the timept occurance of [operator inst.] after line1,2
        break
        
        
    


# get wav fileName,  get the end duration,  generate lines of text that contain the audio speach

for audIndex in range(len(wavList)):       # loop thru the wav files
    
#audIndex = 1      # index to loop thru the audio/wav files names

    wav1 = wavList[audIndex]
    wav1 = wav1.split("-")[1].split(",")[0]      # selects the integer part of end time
    
    wav1End = int(wav1)      # int of the end time
                           #WF  operator at 1915s
    if (wav1End > 500) and (wav1End < 830):   #interval around 1080s when [op inst.] start(CME)
        wav1End = wav1End - 50
    elif (wav1End > 830) and (wav1End < 1255):
        wav1End = wav1End - 100
    elif (wav1End > 1255) and (wav1End < 1500):
        wav1End = wav1End - 100
    elif (wav1End > 1500) and (wav1End < 1750):    #### ended at this line for BP
        wav1End = wav1End - 150
    elif (wav1End > 1750) and (wav1End < 2680):
        wav1End = wav1End - 160
    elif (wav1End > 2680) and (wav1End < 3575):
        wav1End = wav1End - 110
    elif (wav1End > 3575) and (wav1End < 5000):
        wav1End = wav1End - 60
        

        
    
    
    
#    ### ======= check endtime  ========= (from previous script)
#    if (wav1End > (float(timeOfOperator)-400)) and (wav1End < float(timeOfOperator)-80):      
#        wav1End = wav1End + 25
#    elif (wav1End > float(timeOfOperator)-80) and (wav1End < 1160):
#        wav1End = wav1End + 65
#    elif (wav1End > 1160) and (wav1End < 2500):    # <--- *******  file/call specific.  can be 4/5 * float(textStop[-1])
#        wav1End = wav1End + 25
#    elif wav1End > 2900:         # ****** <-----  can make this 8/9 * length of call  float(textStop[-1])
#        wav1End = wav1End - 25      # move to "lesser text line position" speach was covered slower than in .stm file
#    
#        ######## needed 2 lines below at 1438s.  +25s.
#        ###      begin adding +25 at ~600s  (400s before operator instructions)     *********
        
        
    lineNumber = -1           # store line number identified for the audio
    
    # get an estimate for the lineNumber of the transcript text
    for i in range(len(textStop)):
        if wav1End < float(textStop[i]):
            lineNumber = i
            break
    
    
    # if the wav1End time  was not less than the last textStop time    
    if lineNumber==-1:     
        lineNumber = len(textStop)-1    # set to the last line
    
    # ^^^^^ lines above in an interval of 50s
    lineNumAbove = max(lineNumber-4,0)        #max( ,0) take max,  get index 0 or higher
    
    if (wav1End-50) > 24:    # if beyond 50s in the text-audio time, and beyond first line (of ~24s)
        
        while (wav1End - 50) < float(textStop[lineNumAbove]):
            lineNumAbove -= 1   # move up one line,    until textStop is 50s or more before center line
            lineNumAbove = max(lineNumAbove,0)
            if lineNumAbove ==0:
                break
            
    
    
    # vvvvvv  lines below, interval of 50s    (instead of a specific number of lines)
    lineNumBelow = min(lineNumber+4,len(textStop)-1)
    
    while (wav1End + 50) > float(textStop[lineNumBelow]):
        lineNumBelow += 1  # move down one line
        if lineNumBelow > (len(textStop)-1):           # if beyond the last line
            lineNumBelow = len(textStop)-1
            break
        
        
    
    # write the found line number to the chopped text file,  and lines above/below
    nameChop = wavList[audIndex].split(".wav")[0]
    
    fileTextChop = open("chopped_text_file/" + nameChop + ".txt", "w")
    
    
    if lineNumber == len(textStop)-1:   # if last line
        #write last 8 lines
        fileTextChop.writelines(onlyText[-8:-1])
        fileTextChop.write(onlyText[-1])
        
    else:
        fileTextChop.writelines(onlyText[max(lineNumAbove,0):lineNumber+1])     # lines before, and line
        fileTextChop.writelines(onlyText[min(lineNumber+1,len(onlyText)-1):min(lineNumBelow+1, len(onlyText))])     
        # lines after   unless its the last line
    
        #fileTextChop.write(onlyText[min(lineNumber+2, len(onlyText)-1)])     # 2nd line after  (old version)
        # add 3rd line after (or -- 1 more line b4 the estimate)
    
    
           # if lineNumber is the last one, 313, the last line may be repeated
    
    
    fileTextChop.close()

#if timeEnd is over 1000s , try: add 4 to the line number    (was below by 4 lines (from center lineNumber) for the 1019s audio file)




# check 2nd, 3rd, first few audio files to see if the text matches up


# 3255 last audio file

### check the 1174s mark (transcript.stm), where the operator instructions are




                                   # running after finalized audio, text file chop matching
# convert to mp3 files

#for file in $(ls *wav):
#    ffmpeg -i $file ${file%%.wav}.mp3

#
#for item in wavList:
#    subprocess.call(["ffmpeg", "-i", "chopped_audio_file/" + item, "chopped_audio_file/" + item.split(".wav")[0] + ".mp3" ])
## output: 0  (no errors)   output: 1 (command exiting, does not overwrite)


### ------------------ make 4 parts directories  (after converting to mp3s)  -----------------------
if not os.path.isdir("chopped_files_part1"):
    os.mkdir("chopped_files_part1")
    
if not os.path.isdir("chopped_files_part2"):
    os.mkdir("chopped_files_part2")
    
if not os.path.isdir("chopped_files_part3"):
    os.mkdir("chopped_files_part3")
    
if not os.path.isdir("chopped_files_part4"):
    os.mkdir("chopped_files_part4")
    

### copy text files over into parts folders

numFiles = len(wavList)
indxParts = range(0,numFiles,int(numFiles/4))   # index of start/stop points for the parts

natsortWav = natsort.natsorted(wavList)      # natural sorting of wav files

for i in range(0,len(indxParts)-1):    #begin at 0,end 3.  step size by 105/4
    if i !=len(indxParts)-2:   # len (5) -2
        partList = natsortWav[indxParts[i]:indxParts[i+1]]
    else:  #i=3 (for 4 splits)
        partList = natsortWav[indxParts[i]:]     # 2nd to last index, take list to end
        
    #copy audio over,   text
    for k in range(len(partList)):
        
        audCopy = partList[k].split(".wav")[0] + ".mp3"
        shutil.copy2("chopped_audio_file/" + audCopy, "chopped_files_part" + str(i+1) + "/" + audCopy)
        
        textCopy = partList[k].split(".wav")[0] + ".txt"
        
        shutil.copy2("chopped_text_file/" + textCopy, "chopped_files_part" + str(i+1) + "/" + textCopy)
        
    

        
        
