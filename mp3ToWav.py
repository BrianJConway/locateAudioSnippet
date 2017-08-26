import os
import glob
import re
from pydub import AudioSegment

fortyFiveSecs = 45 * 1000
minute = 60 * 1000

# Path where the podcasts are located
video_dir = os.path.abspath('./mbmbam/')

# File types converting from  
extension_list = ('*.mp3' )

os.chdir(video_dir)
for extension in extension_list:
    for podcastMP3 in glob.glob(extension):
        # Extract .mp3 filename
        mp3_fileName = os.path.splitext(os.path.basename(podcastMP3))[0]

        # Regular expression that finds the episode number
        match = re.search(r'\d+$', mp3_fileName)

        # Checkc if episode number was found
        if match != None:
            wav_filename = 'mbmbam' + match.group() + '.wav'

            # Create podcast object 
            podcast = AudioSegment.from_file(podcastMP3)

            # Check if not already processed
            if wav_filename not in os.listdir('./wav'):
                print('Converting ' + mp3_fileName + '.mp3 to '+  wav_filename + "... ", end='', flush=True )

                # Cut the beginning theme song
                if int(match.group()) <= 172:
                    podcast = podcast[fortyFiveSecs:]
                # Podcasts beyond 172 have ending ads, cut those as well
                else:
                    podcast = podcast[fortyFiveSecs:len(podcast) - minute]

                # Ensure only single channel saved
                podcast = podcast.set_channels(1)

                # Save wav file 
                podcast.export('./wav/' + wav_filename, format='wav')
                print('Done')

        # Delete .mp3 file
        if os.path.isfile(podcastMP3):
            print('Permanently deleting ' + podcastMP3)
            os.unlink('./' + podcastMP3)

print('All Done.')
