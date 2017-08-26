#!/usr/bin/python
import os
import shutil
import pprint
import send2trash
import re

# Done like this because I need image files processed
# in correct numerical order, and sorting the filenames
# alphabetically sorts them wrong

resultsFile = open('y.txt', 'w')

episodeNums = [ ]

for imageFile in os.listdir('chunkImages'):
    match = re.search(r'mbmbam(\d+)_(\d+)(_POS)?.png', imageFile);
    if int(match.group(1)) not in episodeNums:
        episodeNums.append(int(match.group(1)))

print(episodeNums)
episodeNums.sort()

for episode in episodeNums:

    imageFiles = { }
    maxChunk = -1;

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
            shutil.copy('chunkImages/' + imageFiles[chunkNum], 'positiveExamples')
        else:
            resultsFile.write('0 \n')
        shutil.copy('chunkImages/' + imageFiles[chunkNum], 'trainingSetImages')

resultsFile.close()
