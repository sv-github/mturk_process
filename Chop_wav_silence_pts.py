import os
import sys
import wave
import numpy as np
import time
import glob
from sys import exit
import subprocess

MAXIMUM = 16384
MINIMUM = 500
CHOPSIZE = 20    # try increasing to 20s, while makeTranscript to 15s of 'line time'

          #Chop_wav  filename  outputdir  (no slash)

# truncate float
def truncate(f, n):
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return ','.join([i, (d+'0'*n)[:n]])

# get max silence point in file
def getMaxSilence(signal, THRESHOLD,fs):
    def isSilent(amplitude):
        if abs(amplitude) < THRESHOLD:
            return 1
        else:
            return 0

    # Find silence
    Silence = [isSilent(x) for x in signal]

    # Find moments of silence
    # In seconds times fs
    SILENCELENGTH = int(0.2 * fs)
    SILENCEBUFFER = int(0.05 * fs)
    LongSilence = np.zeros(len(Silence))
    SumSilence = np.zeros(len(Silence))

    # go through signal and find if the point matches conditions for silence (based on the length and buffer)
    firstPass = True
    aggregateSilence = 0
    for i in range(len(Silence)):
        if firstPass and Silence[i+SILENCEBUFFER] == 1:
            LongSilence[i] = 0
        elif firstPass:
            firstPass = False

        if i+SILENCEBUFFER < len(Silence):
            aggregateSilence = (aggregateSilence + Silence[i])*Silence[i+SILENCEBUFFER]
        else:
            aggregateSilence = (aggregateSilence + Silence[i])*Silence[i]

        if aggregateSilence > SILENCELENGTH:
            LongSilence[i] = 1

    # find the max silence point
    maxSilence = 0
    longSilenceSum = 0
    SilenceIndex = len(LongSilence)/2
    for i in range(len(LongSilence)):
        if LongSilence[i] == 1:
            longSilenceSum += LongSilence[i]
            if longSilenceSum > maxSilence:
                maxSilence = longSilenceSum
                SilenceIndex = (i - SILENCEBUFFER)/2
        else:
            longSilenceSum = 0

    return SilenceIndex

# get signal given a wav file, start and length
def framesAndSignal(wav, start, length):
    fs = wav.getframerate()
    n_frames = int(start*fs)
    wav.setpos(n_frames)
    n_frames = int(length*fs)
    frames = wav.readframes(n_frames)
    signal = np.fromstring(frames, 'Int16')

    return frames, signal

# write a new wav file segment
def writeWavFile(wf, filename, frames, last=False,count=0):
    f = wave.open(filename, 'wb')
    f.setnchannels(wf.getnchannels())
    f.setsampwidth(wf.getsampwidth())
    f.setframerate(wf.getframerate())
    f.writeframes(frames)
    f.close()
    #t = Thread(target=transcribe, args=(filename,last,count))
    #t.start()

# chop up a file based on silence endpoint
def chopWavFileBySilence(audioStartPoint, audioEndPoint, wf, THRESHOLD, outputFolder, outputfile):
    fs = wf.getframerate()
    length = audioEndPoint-audioStartPoint
    frames, signal = framesAndSignal(wf, audioEndPoint-(length/10),length)
    end=0
    end = getMaxSilence(signal, THRESHOLD,fs)/fs
    newAudioEndPoint = audioStartPoint + (0.9)*length + end
    frames, signal = framesAndSignal(wf, audioStartPoint, (0.9)*length+end)

    writeWavFile(wf, outputFolder + "/" + outputfile + "_" + truncate(audioStartPoint, 3) + "-" + truncate(newAudioEndPoint, 3) + ".wav", frames)

    return newAudioEndPoint

def makeChoppedWavFiles(filename, outputFolder):
    outputfile = filename.split("/")[-1].split(".")[0]
    # open the initial given wave file
    wf = wave.open(filename, 'r')
    fs = wf.getframerate()
    duration = int(wf.getnframes() / float(fs))
    frames = wf.readframes(-1)
    signal = np.fromstring(frames, 'Int16')

    # get the silence threshold               # commented out logging command
    #print("Getting threshold value from silence (this can take a while for large files)...")
    ########logging.info("Getting threshold value from silence for file {}".format(filename))
    THRESHOLD = max([MINIMUM/MAXIMUM * max(abs(signal)), MINIMUM])

    # loop through five second segments of file
    start = 0
    length = min(CHOPSIZE,duration)
    count = 1
    while start < int(duration/length)*length-length:
        #print("Chopping file at " + truncate(start,3) + " with max length " + truncate(length,3) + " of total length " + str(int(duration/length)*length))
        ########logging.info("Chopping file at {}".format(start))
        newstart = chopWavFileBySilence(start, start+length, wf, THRESHOLD, outputFolder, outputfile)
        start = newstart
        count += 1

    # take care of the last segment of the file if there is one
    if duration > start:
        # last segment of file
        frames, signal = framesAndSignal(wf, start, (duration-start))

        writeWavFile(wf, outputFolder + "/" + outputfile + "_" + truncate(start,3) + "-" + truncate(duration,3) + ".wav", frames, True, count)

    wf.close()
	
def main():
	try:
		filename = sys.argv[1]
	except IndexError:
		print("No filename specified")
		exit(1)
		
	try:
		outputdir = sys.argv[2]
	except IndexError:
		print("No output directory specified")
		exit(1)
		
	makeChoppedWavFiles(filename,outputdir)
 
     # remove operator audio from the first chopped file (see below, CME call only)
     
	
if __name__ == '__main__':
	main()
 
 
 
 
 
 
 
 # 1st file has the operator and 2nd speaker, separated by silence
 #  can use the ffmpeg silenceremover to cut out the operator
 
# glob.glob( fileName ,   *0,00*)
# ffmpeg command
# ffmpeg -i CME2016call_0,000-22,411.wav -af silenceremove=1:1.5:-50dB CME2016_1stFileCut.wav
# 
# subprocess.call(["ls", "-l", "/etc/resolv.conf"])
# 
# 
# file1 = glob.glob(outputdir + "/*_0,000*")
# 
# subprocess.call(["ffmpeg", "-i", file1, "-af",  "silenceremove=1:1.5:-50dB", "/Users/svyatvergun/Documents/pythonAudioTraining/mturk_processing/CME2016_1stFileCut.wav"])
 #Out 0 -- no errors                                     # tried 2 "signal" segments 0.5s or more in duration
 
 # ------> may only be needed for the CME call. CBOE and BAC had the 1st speaker speek for 20s+
 
 