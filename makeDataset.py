import os, sys
from pydub import AudioSegment
import numpy as np
import spectrogram, genLabels
from matplotlib import pyplot as plt
import natsort
import genLabels

def cutEndsOff(podcastFile):
    twentyOneMins27Secs = (21 * 60  + 27) * 1000
    seventeenMins = 17 * 60 * 1000
    podcast = AudioSegment.from_wav(podcastFile)
    podcast = podcast[twentyOneMins27Secs:len(podcast) - seventeenMins]
    podcast.export("current.wav", format="wav")

    return podcast

# Generate flattened 50x100 matrix of current chunk
def processChunk(chunkData):
    chunkHeight = int(chunkData.shape[0] / 50)
    chunkWidth = int(chunkData.shape[1] / 100)

    avgVals = np.zeros((50,100))

    for row in range(len(avgVals)):
        for col in range(len(avgVals[row])):
            
            rowStart = row * chunkHeight
            rowEnd = rowStart + chunkHeight
            colStart = col * chunkWidth
            colEnd = colStart + chunkWidth

            currentChunk = chunkData[rowStart:rowEnd,colStart:colEnd]
            avgVals[row][col] = np.mean(currentChunk)

    return avgVals.flatten()

def makeImage(chunkData, fileName, colormap="jet"):
    plt.figure(figsize=(2, 1),dpi=60)
    plt.imshow(chunkData, origin="lower", aspect="auto", cmap=colormap, interpolation="none")

    plt.xticks([])
    plt.yticks([])

    plt.savefig( os.path.join('chunkImages', fileName + '.png'), dpi='figure', bbox_inches="tight", pad_inches=0)
            
    plt.clf()
    plt.close()

def splitIntoChunks(podcastData, podcastAudio, fileName, genImages=False, genAudioSnippets=False):
    strideSeconds = 6
    chunkDurationSeconds = 13

    rowsPerChunk = podcastData.shape[0]
    columnsPerSecond =  podcastData.shape[1] / podcastAudio.duration_seconds 
    columnsPerChunk = int(chunkDurationSeconds * columnsPerSecond)

    trainingExamples = open('X.txt', 'a')

    print('File: ' + fileName)
    print('Duration: ' + str(int(podcastAudio.duration_seconds)) +' seconds.')

    lastChunk = int(podcastAudio.duration_seconds / strideSeconds)

    for chunk in range(lastChunk):
        print('Processing Chunk ' + str(chunk) + '/' + str(lastChunk - 1))
        rowStart = 0
        rowEnd = 513
        colStart = chunk * (strideSeconds * columnsPerSecond)
        colEnd = colStart + columnsPerChunk

        chunkData = podcastData[rowStart:rowEnd,colStart:colEnd]

        if genImages:
            # Create image folder if it doesn't exist
            os.makedirs('chunkImages', exist_ok=True)

            # Create image for current cunk
            makeImage(chunkData, fileName[:-4] + '_' + str(chunk))

        if genAudioSnippets:
            # Create folder for audio snippets if it doesn't exist
            os.makedirs('chunkAudioFiles', exist_ok=True)

            # Create wav file for current cunk
            chunkData.export(os.path.join('chunkAudioFiles', fileName[:-4] + '_' + str(chunk) + '.wav'), format='wav')

        # Get matrix of averaged values for the current chunk unrolled into a single row of values
        singleRow = processChunk(chunkData)

        # Append row contents to 'X' file
        for currentVal in singleRow:
            trainingExamples.write(str(currentVal) + ' ')
        trainingExamples.write('\n')

    trainingExamples.close()

def fromScratch(path, genImages=True, genAudioSnippets=False):
    # Get naturally sorted list of wav files
    files = os.listdir(path)
    sortedFiles = natsort.natsorted(files)
    
    for fileName in sortedFiles:
        # Get audio of just the middle section
        middleSegment = cutEndsOff(os.path.join(path, fileName))

        print('File: ' + fileName)
        print('Duration: ' + str(middleSegment.duration_seconds) )

        # Short time Fourier Transform of podcast file
        audioData = spectrogram.plotstft('current.wav')

        # Add current episode chunks to 'X' matrix of averaged values for each chunk of the audio
        splitIntoChunks(audioData, middleSegment, fileName, genImages=genImages, genAudioSnippets=genAudioSnippets)

def fromLabeledData(path):
    # Load dictionary of all episodes and their positive chunks
    posExamples = genLabels.loadChunksFile()
    
    # Loop through each episode
    for episodeNum in posExamples.keys():
        # Only process episodes that actually have positive chunks
        if len(posExamples[episodeNum]) > 0:    
            fileName = 'mbmbam' + str(episodeNum) + '.wav'

            # Get audio of just the middle section
            middleSegment = cutEndsOff(os.path.join(path, fileName))

            # Generate 'y' file for current episode 
            genLabels.labelOneEpisode(middleSegment, episodeNum, posExamples[episodeNum])

            print('File: ' + fileName)
            print('Duration: ' + str(middleSegment.duration_seconds) )

            # Short time Fourier Transform of podcast file
            audioData = spectrogram.plotstft('current.wav')

            # Add current episode chunks to 'X' matrix of averaged values for each chunk of the audio
            splitIntoChunks(audioData, middleSegment, fileName)

    # Combine each episode's 'y' file into one big 'y' file
    genLabels.combileFiles()

#fromScratch('/media/linux/Flash/mbmbam/')
#fromLabeledData('/media/linux/Flash/mbmbam/')