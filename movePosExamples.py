#!/usr/bin/python
import os
import send2trash
import shutil

# Create sorted list of image files
imgFiles = os.listdir('chunkImages')
imgFiles.sort()

posFiles = os.listdir('positiveExamples')
posFiles.sort()

for img in posFiles:
    stem = img[:-8] + '.png'
    if stem in imgFiles:
        print('Deleting ...' + stem)
        send2trash.send2trash('./chunkImages/' + stem)
        print('Copying ...' + img)
        shutil.copy('./positiveExamples/' + img, './chunkImages/')

