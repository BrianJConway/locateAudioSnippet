import pprint
import re
import natsort
import send2trash
import os
from pydub import AudioSegment


path = '/media/linux/Flash/mbmbam/'


def loadChunksFile():
    # Read chunk info for each episode into dictionary
    chunksFile = open('episodeChunks.txt')

    # Read each line of file into string
    lines = chunksFile.readlines()

    posExamples = {}
    for currentLine in lines:
        values = currentLine.split()
        episode = int(values[0][:-1])
        posExamples.setdefault(episode, [])

        for chunkIndex in range(1, len(values)):
            posExamples[episode].append(int(values[chunkIndex]))
    chunksFile.close()

    return posExamples


def labelOneEpisode(episodeAudio, episodeNum, posChunks):
    labelsFile = open('/home/linux/Desktop/AdFinder/dataLabels/' +
                      str(episodeNum) + 'y.txt', 'w')
    podcastDuration = episodeAudio.duration_seconds - \
        (21 * 60 + 27) - (17 * 60)
    numChunks = podcastDuration / 6

    print('Episode ' + str(episodeNum) +
          ': ' + str(int(numChunks)) + ' chunks.')
    for chunkNum in range(int(numChunks)):
        if chunkNum in posChunks:
            labelsFile.write('1 \n')
        else:
            labelsFile.write('0 \n')
    labelsFile.close()


def combileFiles():
    labelsFiles = os.listdir('dataLabels')
    sortedFiles = natsort.natsorted(labelsFiles)

    # Combine all label files to create one giant file of labels
    allLabels = open('/home/linux/Desktop/AdFinder/dataLabels/y.txt', 'w')
    for currentFile in sortedFiles:
        labelsFile = open('dataLabels/' + currentFile)
        episodeLabels = labelsFile.read()
        allLabels.write(episodeLabels)
        labelsFile.close()
    allLabels.close()


def fromTxtFile():
    posExamples = loadChunksFile()

    if 'dataLabels' not in os.listdir():
        os.makedirs('dataLabels')

    # Generate labels file for current episode
    for currentEpisode in posExamples.keys():
        if len(posExamples[currentEpisode]) > 0:
            episodeAudio = AudioSegment.from_wav(
                path + 'mbmbam' + str(currentEpisode) + '.wav')
            labelOneEpisode(episodeAudio, currentEpisode, posExamples[currentEpisode])
            
    combileFiles()


fromTxtFile()


def fromImages():
    resultsFile = open('y.txt', 'w')

    episodeNums = []

    for imageFile in os.listdir('chunkImages'):
        match = re.search(r'mbmbam(\d+)_(\d+)(_POS)?.png', imageFile)
        if int(match.group(1)) not in episodeNums:
            episodeNums.append(int(match.group(1)))

    print(episodeNums)
    episodeNums.sort()

    for episode in episodeNums:

        imageFiles = {}
        maxChunk = -1

        for imageFile in os.listdir('chunkImages'):
            # Get chunk number from file name
            match = re.search(str(episode) + r'_(\d+).', imageFile)

            if match:
                chunkNumber = int(match.group(1))

                # Check if new max chunk value
                if maxChunk < chunkNumber:
                    maxChunk = chunkNumber

                # Save chunk and filename in dictionary
                imageFiles[int(chunkNumber)] = imageFile

        for chunkNum in range(maxChunk + 1):
            print('Processing ' + imageFiles[chunkNum] + '...')
            if imageFiles[chunkNum].endswith('POS.png'):
                resultsFile.write('1 \n')
                shutil.copy('chunkImages/' +
                            imageFiles[chunkNum], 'positiveExamples')
            else:
                resultsFile.write('0 \n')
            shutil.copy('chunkImages/' +
                        imageFiles[chunkNum], 'trainingSetImages')

    resultsFile.close()


"""
timings = {}

for i in range(len(line)):
    # remove newlines from end of each string
    line[i] = line[i][:-1]

    # Find episode number, minutes, and seconds
    match = re.search(r'mbmbam(\d+).wav: (\d+):(\d+)', line[i]);
    episode = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))

    timings.setdefault(episode, [])
    totalSeconds = minutes * 60 + seconds
    currentExample = {'minutes': minutes, 'seconds': seconds,
                      'totalSeconds': totalSeconds, 'chunk': (totalSeconds - 1287) / 6}
    timings[episode].append(currentExample)

times = open('oldTimings', 'w')

for episode in timings.keys():
    times.write(str(episode) + ': ')
    for example in timings[episode]:
        times.write(str(example['chunk'])[:-2] + ' ')
    times.write('\n')
times.close()

episodes = timings.keys()

path = '/media/linux/Flash/mbmbam/'

thirteenSeconds = 13 * 1000

for episode in timings.keys():
    delete = []
    if len(timings[episode]) == 1:
        episodeAudio = AudioSegment.from_wav(
            path + 'mbmbam' + str(episode) + '.wav')
        for example in timings[episode]:
            chunkStart = example['totalSeconds'] * 1000
            chunkEnd = chunkStart + thirteenSeconds

            chunk = episodeAudio[chunkStart:chunkEnd]
            fileName = str(episode) + '_' + str(example['chunk']) + '.wav'
            chunk.export('located/' + fileName, format="wav")

        for example in timings[episode]:
            fileName = str(episode) + '_' + str(example['chunk']) + '.wav'
            print(fileName + ': is this chunk valid? (Y/N)')
            valid = input()

            if valid.upper() == 'N':
                print('Deleting ' + fileName + '...')
                send2trash.send2trash('located/' + fileName)
                delete.append(example)

    for item in delete:
        timings[episode].remove(item)

times = open('newTimings.txt', 'a')

for episode in timings.keys():
    times.write(str(episode) + ': ')
    for example in timings[episode]:
        times.write(str(example['chunk'])[:-2] + ' ')
    times.write('\n')
times.close()

"""
