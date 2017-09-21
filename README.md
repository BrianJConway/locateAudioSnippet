# Locate Audio Snippet
Supervised machine learning project that uses regularized logistic regression to find when a specific 13 second audio jingle plays in a podcast.

# Background
The podcast "My Brother, My Brother, and Me" always plays a jingle when their advertisements section begins, this project uses machine learning to find what time the jingle plays in any particular episode. There are python scripts to download the episodes, create a dataset from the available episodes, train a logistic regression classifier on the dataset, and generate timings for each episode based on the learned parameters. 

# Description

## Downloading the episodes

### downMBMBAM.py
Downloads episodes of the podcast. The script allows you to specify start and end dates for the episodes you want.

### mp3ToWav.py
Converts the .mp3 files to .wav files for the rest of the scripts to be able to process the audio.

## Creating a labeled dataset

### makeDataset.py 
Takes each episode and splits it into 13 second chunks with a six second sliding window. Performs a short-time fourier transform on the chunks in order to get numerical data on each chunk as a matrix of values. Each matrix is flattened and put onto a single line of the overall "X" matrix of training examples. The "from scratch" option should be used when initially creating the dataset, since it will also generate spectrogram images of each chunk, which will be used to hand-label the postiive examples. The "X" matrix is stored in a file called 'X.txt' and a compressed numpy file called 'data.npz'.

### genLabels.py
This is responsible for generating a "y" matrix of labels for the training examples. The fromScratch() function is used to loop through the image files and label the chunks as positive examples or negative examples based on their filenames. Before running it, you should look through the chunk images and simply add "_POS" to the names of any images that represent positive examples. The labels will be put into a file called "y.txt".

## Training a logistic regression classifier on the dataset

### logisticReg.py
Takes the "X" matrix of training examples and the "y" matrix of labels and uses logisitc regression to train a classifier to recognize the audio chunks that represent the jingle we're looking for. The output is a "theta" matrix of learned parameters in the compressed numpy file "theta.npz".

## Using the learned parameters to find timings for the jingle

### locateAudio.py
Takes either a single episode or an entire dataset and uses the learned "theta" parameters to generate a list of timings that the jingle occurs (or in the case of the single episode, one timing).