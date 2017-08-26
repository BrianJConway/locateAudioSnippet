import os
from pydub import AudioSegment
import numpy as np
import spectrogram
from matplotlib import pyplot as plt

def cutEndsOff(podcastFile):
    twentyOneMins = 21 * 60 * 1000
    seventeenMins = 17 * 60 * 1000
    podcast = AudioSegment.from_wav('./wav/' + podcastFile)
    podcast = podcast[99*13*1000:len(podcast) - seventeenMins]
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

    plt.savefig( 'chunkImages/' + fileName + '.png', dpi='figure', bbox_inches="tight", pad_inches=0)
            
    plt.clf()
    plt.close()

def splitIntoChunks(podcastData, podcastAudio, fileName):
    printImg = True

    strideSeconds = 6
    chunkDurationSeconds = 13
    num_chunks = int(podcastAudio.duration_seconds / chunkDurationSeconds)

    rowsPerChunk = podcastData.shape[0]
    columnsPerSecond =  podcastData.shape[1] / podcastAudio.duration_seconds 
    columnsPerChunk = int(chunkDurationSeconds * columnsPerSecond)

    trainingExamples = open('X.txt', 'a')

    print('File: ' + fileName)
    print('Duration: ' + str(int(podcastAudio.duration_seconds)) +' seconds.')
    print('Chunks: ' + str(num_chunks))

    lastChunk = int(podcastAudio.duration_seconds / strideSeconds)

    for chunk in range(lastChunk + 1):
        print('Processing Chunk ' + str(chunk) + '/' + str(lastChunk))
        rowStart = 0
        rowEnd = 513
        colStart = chunk * (strideSeconds * columnsPerSecond)
        colEnd = colStart + columnsPerChunk

        chunkData = podcastData[rowStart:rowEnd,colStart:colEnd]

        if printImg:
            makeImage(chunkData, fileName[:-4] + '_' + str(chunk))

        singleRow = processChunk(chunkData)

        for currentVal in singleRow:
            trainingExamples.write(str(currentVal) + ' ')
        trainingExamples.write('\n')

    trainingExamples.close()

sortedFiles = os.listdir('./wav')
sortedFiles.sort()

for fileName in sortedFiles:
    middleSegment = cutEndsOff(fileName)

    print('File: ' + fileName)
    print('Duration: ' + str(middleSegment.duration_seconds) )

    # Short time Fourier Transform of podcast file
    audioData = spectrogram.plotstft('current.wav')

    splitIntoChunks(audioData, middleSegment, fileName)