import pprint, re, natsort, send2trash, os, shutil
from pydub import AudioSegment

# Creates a dictionary of episode numbers as keys and lists of
# chunk numbers for that episode as values
# File format for each line: "EPISODENUM: chunk1 chunk2 ... chunkN"
def loadChunksFile():
    # Read chunk info for each episode into dictionary
    chunksFile = open('episodeChunks.txt')

    # Read each line of file into string
    lines = chunksFile.readlines()

    posExamples = {}
    for currentLine in lines:
        # Get list of each word in the line
        values = currentLine.split()

        # Get the episode number, removing the colon at the end
        episode = int(values[0][:-1])
        posExamples.setdefault(episode, [])

        # Get each chunk number, add to list of chunks for that episode
        for chunkIndex in range(1, len(values)):
            posExamples[episode].append(int(values[chunkIndex]))
    chunksFile.close()

    return posExamples


def labelOneEpisode(episodeAudio, episodeNum, posChunks):
    labelsFile = open(os.path.join('dataLabels', str(episodeNum) + 'y.txt'), 'w')
    podcastDuration = episodeAudio.duration_seconds
    numChunks = podcastDuration / 6

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
    allLabels = open(os.path.join('dataLabels', 'y.txt'), 'w')
    for currentFile in sortedFiles:
        labelsFile = open(os.path.join('dataLabels', currentFile), 'r')
        episodeLabels = labelsFile.read()
        allLabels.write(episodeLabels)
        labelsFile.close()
    allLabels.close()


def fromTxtFile(path):
    posExamples = loadChunksFile()

    os.makedirs('dataLabels', exist_ok=True)

    # Generate labels file for current episode
    for currentEpisode in posExamples.keys():
        if len(posExamples[currentEpisode]) > 0:
                twentyOneMins27Secs = (21 * 60  + 27) * 1000
                seventeenMins = 17 * 60 * 1000
                episodeAudio = AudioSegment.from_wav(os.path.join(path, 'mbmbam' + str(currentEpisode) + '.wav'))
                episodeAudio = episodeAudio[twentyOneMins27Secs:len(episodeAudio) - seventeenMins]
                labelOneEpisode(episodeAudio, currentEpisode, posExamples[currentEpisode])
    # combileFiles()

def fromImages():
    os.makedirs('positiveExamples', exist_ok=True)
    os.makedirs('dataLabels', exist_ok=True)

    # Get sorted list of all episodes that are represented by images
    episodeFiles = { }
    allFiles = os.listdir('chunkImages')
    allFiles = natsort.natsorted(allFiles)

    for imageFile in allFiles:
        match = re.search(r'mbmbam(\d+)_(\d+)(_POS)?.png', imageFile)
        episodeNumber = int(match.group(1))
        episodeFiles.setdefault(episodeNumber, [ ])
        episodeFiles[episodeNumber].append(match.group())
    
    # Create y matrix in file that labels positive examples
    resultsFile = open('y.txt', 'w')
    for episode in episodeFiles.keys():
        episodeFile = open(os.path.join('dataLabels', str(episode) + 'y.txt' ), 'w')
        for imageFile in episodeFiles[episode]:
            print('Processing ' + imageFile + '...')
            if imageFile.endswith('POS.png'):
                resultsFile.write('1 \n')
                episodeFile.write('1 \n')
                shutil.copy(os.path.join('chunkImages', imageFile), 'positiveExamples')
            else:
                resultsFile.write('0 \n')
                episodeFile.write('0 \n')
        episodeFile.close()
    resultsFile.close()

    # Create file that shows which chunk numbers are positive for each episode
    chunksFile = open('episodeChunks.txt', 'w')
    for episode in episodeFiles.keys():
        # Write episode number 
        chunksFile.write(str(episode) + ': ')
        # Write current chunk number if the image is labeled as a positive example
        for imageFile in episodeFiles[episode]:
            match = re.search(r'mbmbam(\d+)_(\d+)(_POS)?.png', imageFile)
            if imageFile.endswith('POS.png'):
                chunksFile.write(match.group(2) + ' ')
        chunksFile.write('\n')
    chunksFile.close()