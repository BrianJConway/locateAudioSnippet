import os, glob, re, sys, natsort, send2trash
from pydub import AudioSegment

fortyFiveSecs = 45 * 1000
minute = 60 * 1000

# Path where the mp3's are located
if len(sys.argv) > 1:
    srcPath = sys.argv[1]
else:
    srcPath = 'mp3'

# Path where the wav files will be stored
if len(sys.argv) > 2:
    destPath = sys.argv[2]
else:
    destPath = 'wav'

os.makedirs(destPath, exist_ok=True)

# Sort files in source folder
mp3Files = os.listdir(srcPath)
mp3Files = natsort.natsorted(mp3Files)
print(mp3Files)

for fileName in mp3Files:
    if fileName.endswith('.mp3'):
        # Regular expression that finds the episode number
        match = re.search(r'\d+$', fileName[:-4])

        # Check if episode number was found
        if match != None:
            wavFileName = 'mbmbam' + match.group() + '.wav'

            # Check if not already processed
            if wavFileName not in os.listdir(destPath):
                print('Converting ' + fileName + ' to '+  wavFileName + "... ", end='', flush=True )

                # Create podcast object 
                podcast = AudioSegment.from_file(os.path.join(srcPath, fileName))

                # Cut the beginning theme song
                if int(match.group()) <= 172:
                    podcast = podcast[fortyFiveSecs:]
                # Podcasts beyond 172 have ending ads, cut those as well
                else:
                    podcast = podcast[fortyFiveSecs:len(podcast) - minute]

                # Ensure only single channel saved
                podcast = podcast.set_channels(1)

                # Save wav file 
                podcast.export(os.path.join(destPath, wavFileName), format='wav')
                print('Done')

            # Delete .mp3 file
            print('Permanently deleting ' + fileName)
            send2trash.send2trash(os.path.join(srcPath,fileName))

print('All Done.')