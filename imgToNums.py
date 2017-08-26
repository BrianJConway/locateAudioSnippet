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

# Create sorted list of image files
imageFiles = { }
maxChunk = -1

for imageFile in os.listdir('chunkImages'):
    # Get chunk number from file name
    match = re.search(r'_(\d+).', imageFile)
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
    else:
        resultsFile.write('0 \n')
    shutil.copy('chunkImages/' + imageFiles[chunkNum], 'trainingSetImages')

resultsFile.close()