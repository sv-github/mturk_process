#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Read in mturk worker output file,  separate by " > ".  write separate text files that match the corresponding audio files

# assumed directories:      chopped_files_part#,    worker_output_part#
# assumed existing files:            full_text.txt

import glob
import os
import natsort

# ***** directory of worker-part output **** edit part here

dir = "worker_output_part3/"           # working directory of worker's full_text, chopped_text (processed) will be output here 
# ***** --------------------

# ***** change   transName  transSpeaker  below


# store lines for each audio-text pair
fileIn = open(dir + "full_text.txt","r")

line = fileIn.readlines()    # one long line provided by worker

fileIn.close()


lines = line[0].lower().split(" > ")      # 33 lines given  (CBOE)    #lower case each line


fileOut = open(dir + "full_text_lines.txt", "w")

for wline in lines:
    fileOut.write(wline + "\n")   

    
fileOut.close()



# write individual files with time points,   use list of files from part3 folder   (chopped_files_part3)

#fileNames = os.listdir("/Users/svyatvergun/Documents/pythonAudioTraining/mturk_processing/chopped_files_part3")


                                                                         
               # sorted alphabetically,  and "natural order" as appears in mac finder
                                                             #part#/
fileNames = natsort.natsorted(glob.glob("chopped_files_" + dir.split("_")[2] + "*.txt"))



for i in range(len(fileNames)):
    fileNames[i] = fileNames[i].split("/")[-1]      # keep the last part, the text's name
    

# make directory in worker_output to hold chopped text files
if not os.path.isdir(dir + "chopped_text/"):
    os.mkdir(dir + "chopped_text")
    

    
if len(fileNames)!= len(lines):
    print("Number of lines does not match the number of text files from batch folder")
else:
    # write text files to worker_output_part#/chopped_text/ for each line.   keeping the time points in the file name
    for i in range(len(lines)):
        fileWrite = open(dir + "chopped_text/" + fileNames[i],"w")
        fileWrite.write(lines[i].strip())                  
        
        fileWrite.close()


        
    




###   replace it's with it is     we're with  we are
###   replace &   with  and
###   remove '?'
###   remove - 
###   remove " ' "

###   replace "q1" with "q one",  "q 1" with "q one"

### check for words not in the dictionary



#### next reassemble texts into .stm format
#CME2016earnTranscript 1 operator 0 11.35 <o,f0,male> good day and welcome to the cme group first quarter two thousand and sixteen earnings call i would like to turn the conference over to john peschier please go ahead sir




### assemble parts into stm formatted file


stmLines = []    # list to hold stm format lines


transName = "WFC2016earnTranscriptMturk"       # with 1 after name
channel = "1"
speakerName = "WFCgeneralspkr"               # general speaker name (audio files contains multiple speakers)
genderTag = "<o,f0,male>"

for i in range(len(lines)):
                               #split at -,  get start and stop times
    timeStart1 = fileNames[i].split("-")[0].split("_")[-1].split(",")[0]         # '2391'
    timeStart2 = fileNames[i].split("-")[0].split("_")[-1].split(",")[1]; timeStart2 = timeStart2[0:3]   # 3 digits after decimal
    timeStart = ".".join([timeStart1, timeStart2])
    
    timeStop1 = fileNames[i].split("-")[1].split(",")[0]
    timeStop2 = fileNames[i].split("-")[1].split(",")[1]; timeStop2 = timeStop2[0:3]
    timeStop = ".".join([timeStop1, timeStop2])
    
    
    
    workline = " ".join([transName, channel, speakerName, timeStart, timeStop, genderTag, lines[i].strip()])
    
    stmLines.append(workline)    # append to stmLines list, prepare to write to file



# then open File,  write lines stmLines 
fileStm = open(dir + transName + dir.split("_")[2][-2] +  ".stm", "w")     #CME2016earnTranscriptMturk#  [-2] 2nd to last char
    
for line in stmLines:
    print(line, file=fileStm)    #print preferred over file.write.  print preserves the line breaks for more cases

fileStm.close()

            #part1,2,3,4   add together to one stm file as the parts are completed

# run validateData.py   after stm file is created     (pull latest valdateData.py )

# if weird word is in there, add to dict  (see below)




# convert audio to sph       
# sox file.wav -c 1 -r 16000 file.sph

# make sure audio and stm names match

#  CME2016earnTranscriptMturk.sph,    CME2016earnTranscriptMturk.stm

# add words to end of dictionary,  multiple pronounciations


## if a plural word is not in dict.   can split the s with a space.   products (not in dict)  -->  product s  