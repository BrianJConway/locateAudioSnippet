import os
import sys
import re
import natsort
from pydub import AudioSegment
import numpy as np
import spectrogram
import genLabels
from matplotlib import pyplot as plt
import subprocess
import shutil
import send2trash


def cutEndsOff(podcastFile):
    twentyOneMins27Secs = (21 * 60 + 27) * 1000
    seventeenMins = 17 * 60 * 1000
    podcast = AudioSegment.from_wav(podcastFile)
    podcast = podcast[twentyOneMins27Secs:len(podcast) - seventeenMins]
    podcast.export("current.wav", format="wav")

    return podcast


'''
 Generate flattened 50x100 matrix of current chunk
 50x100 is chosen arbitrarily since originally
 got chunk data was taken from images that were
 of that resolution, as the algorithm
 works well enough currently, maybe
 experiment with how much smaller the matrix
 can be, in order to reduce memory needed to store
'''


def processChunk(chunkData):
    chunkHeight = int(chunkData.shape[0] / 50)
    chunkWidth = int(chunkData.shape[1] / 100)

    avgVals = np.zeros((50, 100))

    for row in range(len(avgVals)):
        for col in range(len(avgVals[row])):

            rowStart = row * chunkHeight
            rowEnd = rowStart + chunkHeight
            colStart = col * chunkWidth
            colEnd = colStart + chunkWidth

            currentChunk = chunkData[rowStart:rowEnd, colStart:colEnd]
            avgVals[row][col] = np.mean(currentChunk)

    return avgVals.flatten()


def makeImage(chunkData, fileName, colormap="jet"):
    plt.figure(figsize=(2, 1), dpi=60)
    plt.imshow(chunkData, origin="lower", aspect="auto",
               cmap=colormap, interpolation="none")

    plt.xticks([])
    plt.yticks([])

    plt.savefig(os.path.join('chunkImages', fileName + '.png'),
                dpi='figure', bbox_inches="tight", pad_inches=0)

    plt.clf()
    plt.close()


def splitIntoChunks(podcastData, podcastAudio, fileName, genImages=False, genAudioSnippets=False):
    strideSeconds = 6
    chunkDurationSeconds = 13

    rowsPerChunk = podcastData.shape[0]
    columnsPerSecond = podcastData.shape[1] / podcastAudio.duration_seconds
    columnsPerChunk = int(chunkDurationSeconds * columnsPerSecond)

    trainingExamples = open('X.txt', 'a')

    match = re.search(r'mbmbam(\d+).wav', fileName)
    episodeNum = match.group(1)
    episodeFile = open(os.path.join('episodeData', episodeNum + 'X.txt'), 'w')

    print('File: ' + fileName)
    print('Duration: ' + str(int(podcastAudio.duration_seconds)) + ' seconds.')

    lastChunk = int(podcastAudio.duration_seconds / strideSeconds)

    for chunk in range(lastChunk):
        print('Processing Chunk ' + str(chunk) + '/' + str(lastChunk - 1))
        rowStart = 0
        rowEnd = 513
        colStart = chunk * (strideSeconds * columnsPerSecond)
        colEnd = colStart + columnsPerChunk

        chunkData = podcastData[rowStart:rowEnd, colStart:colEnd]

        if genImages:
            # Create image folder if it doesn't exist
            os.makedirs('chunkImages', exist_ok=True)

            # Create image for current cunk
            makeImage(chunkData, fileName[:-4] + '_' + str(chunk))

        if genAudioSnippets:
            # Create folder for audio snippets if it doesn't exist
            os.makedirs('chunkAudioFiles', exist_ok=True)

            audioStart = chunk * strideSeconds * 1000
            audioEnd = audioStart + chunkDurationSeconds * 1000
            chunkAudio = podcastAudio[audioStart:audioEnd]

            # Create wav file for current chunk
            chunkAudio.export(os.path.join(
                'chunkAudioFiles', fileName[:-4] + '_' + str(chunk) + '.wav'), format='wav')

        # Get matrix of averaged values for the current chunk unrolled into a
        # single row of values
        singleRow = processChunk(chunkData)

        # Append row contents to 'X' file
        for currentVal in singleRow:
            trainingExamples.write(str(currentVal) + ' ')
            episodeFile.write(str(currentVal) + ' ')
        trainingExamples.write('\n')
        episodeFile.write('\n')

    episodeFile.close()
    trainingExamples.close()

# Saves 'X.txt' to compressed numpy file
def saveDataset():
    # Check if file size exceeds 1GB
    if os.path.getsize('X.txt') >= 1000000000:
        # Create directory for split chunks
        os.makedirs('splitFile', exist_ok=True)
        shutil.copy('X.txt', 'splitFile')

        # Split X.txt into multiple chunks
        # NOTE: calls linux command, uses linux path structure, will only work
        # on linux
        subprocess.call(["split", "./splitFile/X.txt", "-d",
                         "-l", "15000", "./splitFile/"])

        # Load each chunk and concatenate onto numpy matrix
        index = 0
        chunkFiles = os.listdir('splitFile')
        chunkFiles = natsort.natsorted(chunkFiles)
        for splitChunk in chunkFiles:
            print(splitChunk)
            currentMatrix = np.loadtxt('splitFile/' + splitChunk)

            if index == 0:
                X = currentMatrix
            else:
                X = np.concatenate((X, currentMatrix), axis=0)
            index += 1
            print(X.shape)

        # Save matrix to compresssed .npz file
        np.savez_compressed('data', X=X)
        
    # Otherwise, assume file size is less than 1GB
    else:
        # Load X.txt into numpy matrix and save to .npz file
        X = np.loadtxt('X.txt')
        np.savez_compressed('data', X=X)

def fromScratch(path, genImages=True, genAudioSnippets=False):
    # Get naturally sorted list of wav files
    files = os.listdir(path)
    sortedFiles = natsort.natsorted(files)
    os.makedirs('episodeData', exist_ok=True)

    for fileName in sortedFiles:
        # Get audio of just the middle section
        middleSegment = cutEndsOff(os.path.join(path, fileName))

        print('File: ' + fileName)
        print('Duration: ' + str(middleSegment.duration_seconds))

        # Short time Fourier Transform of podcast file
        audioData = spectrogram.plotstft('current.wav')

        # Add current episode chunks to 'X' matrix of averaged values for each
        # chunk of the audio
        splitIntoChunks(audioData, middleSegment, fileName,
                        genImages=genImages, genAudioSnippets=genAudioSnippets)

        # Save dataset to .npz file
        saveDataset()

def fromLabeledData(path):
    # Load dictionary of all episodes and their positive chunks
    posExamples = genLabels.loadChunksFile()
    os.makedirs('episodeData', exist_ok=True)

    # Loop through each episode
    for episodeNum in posExamples.keys():
        fileName = 'mbmbam' + str(episodeNum) + '.wav'

        # Get audio of just the middle section
        middleSegment = cutEndsOff(os.path.join(path, fileName))

        # Generate 'y' file for current episode
        genLabels.labelOneEpisode(
            middleSegment, episodeNum, posExamples[episodeNum])

        print('File: ' + fileName)
        print('Duration: ' + str(middleSegment.duration_seconds))

        # Short time Fourier Transform of podcast file
        audioData = spectrogram.plotstft('current.wav')

        # Add current episode chunks to 'X' matrix of averaged values for
        # each chunk of the audio
        splitIntoChunks(audioData, middleSegment, fileName)

    # Combine each episode's 'y' file into one big 'y' file
    genLabels.combileFiles()


# fromScratch('wav')
# fromLabeledData('wav')

if os.path.getsize('X.txt') >= 1000000000:
    '''
    # Create directory for split chunks
    os.makedirs('splitFile', exist_ok=True)
    shutil.copy('X.txt', 'splitFile')
    subprocess.call(["split", "./splitFile/X.txt", "-d","-l", "15000", "./splitFile/" ])
    send2trash.send2trash('./splitFile/X.txt')
    '''
