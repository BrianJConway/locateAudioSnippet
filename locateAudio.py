import numpy as np
import math, re, os, sys
import shutil, natsort
from pydub import AudioSegment
import spectrogram
from matplotlib import pyplot as plt

genImages = sys.argv[2]

# Maps values from 0 to 1
def sigmoid(x):
  return 1 / (1 + np.exp(-x))
 
# Normalizes values so that the mean is 0
def normalize(x):
    mu = np.mean(x)
    sigma = np.std(x)
    return (x - mu) / sigma

def cutEndsOff(podcastFile):
    twentyOneMins27Secs = (21 * 60  + 27) * 1000
    seventeenMins = 17 * 60 * 1000
    podcast = AudioSegment.from_wav('./wav/' + podcastFile)
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

    plt.savefig( 'chunkImages/' + fileName + '.png', dpi='figure', bbox_inches="tight", pad_inches=0)
            
    plt.clf()
    plt.close()

def splitIntoChunks(podcastData, podcastAudio, fileName):

    strideSeconds = 6
    chunkDurationSeconds = 13
    num_chunks = int(podcastAudio.duration_seconds / chunkDurationSeconds)

    rowsPerChunk = podcastData.shape[0]
    columnsPerSecond =  podcastData.shape[1] / podcastAudio.duration_seconds 
    columnsPerChunk = int(chunkDurationSeconds * columnsPerSecond)

    trainingExamples = open('X.txt', 'w')

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

        if genImages == "True":
            makeImage(chunkData, fileName[:-4] + '_' + str(chunk))

        singleRow = processChunk(chunkData)

        for currentVal in singleRow:
            trainingExamples.write(str(currentVal) + ' ')
        trainingExamples.write('\n')

    trainingExamples.close()

fileName = sys.argv[1]
middleSegment = cutEndsOff(fileName)

# Short time Fourier Transform of podcast file
audioData = spectrogram.plotstft('current.wav')

splitIntoChunks(audioData, middleSegment, fileName)

# Load X and theta matrices from file
X = np.loadtxt('X.txt')
data = np.load('data.npz')

# Normalize X values
X = normalize(X)

# Add column of ones to front of X
onesCol = np.array([np.ones(X.shape[0])]).T
X = np.concatenate((onesCol, X), axis=1)

# Apply hypothesis function (parameterized by theta) to X
predict = sigmoid(np.dot(X, data['theta'])) >= 0.8

# Find values classified as positive
indexes = np.where(predict == 1)[0]
print('Found ' + str(len(indexes)) + ' positives')

# Get naturally sorted list of file names
files = os.listdir('chunkImages')
sortedFiles = natsort.natsorted(files)

# Print filename corresponding to each index and time
for index in indexes:
    timeSeconds = 45 + (21 * 60) + 17 + index * 6 + 13
    mins, secs = divmod(timeSeconds, 60)
    print(sortedFiles[index])
    print(str(mins) + ':' + str(secs))
