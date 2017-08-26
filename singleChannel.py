from pydub import AudioSegment
import os

for podcastFile in os.listdir('./wav'):

    print('Converting ' + podcastFile + ' to single channel ... ', end='', flush=True )
    podcast = AudioSegment.from_wav('mbmbam/wav/' + podcastFile)
    podcast = podcast.set_channels(1)
    podcast.export('mbmbam/wav/' + podcastFile, format="wav")
    print('Done', flush=True )