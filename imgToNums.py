#!/usr/bin/python
import os
import shutil
import pprint
import send2trash

resultsFile = open('Y.txt', 'a')

# Create sorted list of image files
imgFiles = os.listdir('chunkImages')
imgFiles.sort()

for currentImg in imgFiles:
    print('Processing ' + currentImg + ' ... ', end='', flush=True)
    # Note whether or not this is a positive example
    if currentImg.endswith('POS.png'):
        resultsFile.write('1 \n')
    else:
        resultsFile.write('0 \n')

    print()

resultsFile.close()