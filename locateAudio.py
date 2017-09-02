import numpy as np
import math, re, os, sys, pprint
import shutil, natsort
from pydub import AudioSegment
from matplotlib import pyplot as plt
import spectrogram
import makeDataset

# Maps values from 0 to 1
def sigmoid(x):
  return 1 / (1 + np.exp(-x))

# Normalizes values so that the mean is 0
def normalize(x):
    # Store means of each column in a row vector
    mu = np.mean(x,axis=0)

    # Store std dev of each column in a row vector
    sigma = np.std(x, axis=0)

    # normalize based on mean and std dev of each column
    return (x - mu) / sigma

def applyHypothesis(X, theta, threshold):
    # Normalize X values
    X = normalize(X)
    
    # Add column of ones to front of X
    onesCol = np.array([np.ones(X.shape[0])]).T
    X = np.concatenate((onesCol, X), axis=1)

    # Apply hypothesis function (parameterized by theta) to X
    return sigmoid(np.dot(X, theta)) >= threshold

def locate(fileName, genImages):
    middleSegment = makeDataset.cutEndsOff(fileName)

    # Short time Fourier Transform of podcast file
    audioData = spectrogram.plotstft('current.wav')

    makeDataset.splitIntoChunks(audioData, middleSegment, fileName)

    # Load X and theta matrices from file
    X = np.loadtxt('X.txt')
    data = np.load('data.npz')

    # Apply hypothesis function (parameterized by theta) to X
    predict = applyHypothesis(X, data['theta'], 0.2)

    # Find values classified as positive
    indexes = np.where(predict == 1)[0]
    print( fileName + ':found ' + str(len(indexes)) + ' positives')

    if genImages:
        # Get naturally sorted list of file names
        files = os.listdir('chunkImages')
        sortedFiles = natsort.natsorted(files)

    timesFile = open('times.txt', 'a')

    # Print filename corresponding to each index and time
    for index in indexes:
        timeSeconds = 21 * 60 + 27 + index * 6
        mins, secs = divmod(timeSeconds, 60)
        print(str(mins) + ':' + str(secs))
        timesFile.write(fileName + ': ' + str(mins) + ':' + str(secs) + '\n')
        
        if genImages:
            print(sortedFiles[index])

    timesFile.close()

"""
 Generates a dictionary where episode numbers are keys and the values are a dictionary 
 representing the ranges of indices in X that represent the chunks of that episode
 NOTE: Need to look into using an interval tree to reduce the amount of memory taken up by this
"""
def getDatasetIndices():
    chunkIndices = { }

    index = 0
    files = os.listdir('dataLabels')
    sortedFiles = natsort.natsorted(files)
    for fileName in sortedFiles:
        if not fileName.startswith('y'):
            match = re.search(r'(\d+)y.txt', fileName)
            currentEpisode = int(match.group(1))
            
            currentFile = open('dataLabels/' + fileName)
            numChunks = len(currentFile.readlines())

            chunkIndices[currentEpisode] = { 'start':index, 'end':index + numChunks - 1 }
            index = index + numChunks
    return chunkIndices
            

def locateFromDataset(fileName):
    # Load X, y, and theta matrices
    dataFile = np.load(fileName)
    
    # Reconstruct X from submatrices
    for currentMatrix in dataFile.keys():
        # First submatrix to append to
        if currentMatrix.startswith('x1'):
            X = dataFile['x1']
        # Remaining submatrices get appended
        elif currentMatrix.startswith('x'):
            X = np.concatenate((X, dataFile[currentMatrix]), axis=0)
    
    # Apply hypothesis function to input values, get predictions
    hyp = applyHypothesis(X, dataFile['theta'], 0.2)
    predictions = np.where(hyp == 1)[0] 
    print( 'Found ' + str(len(predictions)) + ' positives')

    # Create a dictionary where each episode has a range of indices in X it corresponds to
    chunkIndices = getDatasetIndices()
    foundChunks = { }

    # Convert indices of X to episode numbers and chunks
    for currentVal in predictions:
        for episode in chunkIndices.keys():
            if currentVal > chunkIndices[episode]['start'] and currentVal < chunkIndices[episode]['end']:
                foundChunks.setdefault(episode,[ ])
                foundChunks[episode].append(currentVal - chunkIndices[episode]['start'])
                

    pprint.pprint(foundChunks)

    # Convert chunks to times for each episode, print to file
    timesFile = open('times.txt', 'w')
    for episode in foundChunks.keys():
        # Get the first found time for the current episode
        timeSeconds = 21 * 60 + 27 + foundChunks[episode][0] * 6
        mins, secs = divmod(timeSeconds, 60)
        timesFile.write('mbmbam' + str(episode) + '.wav' + ': ' + str(mins) + ':' + str(secs) + '\n')
    timesFile.close()

locateFromDataset('data.npz')

"""
path = '/media/linux/Flash/mbmbam/wav'
files = os.listdir(path)
sortedFiles = natsort.natsorted(files)

for audioFile in sortedFiles:
    locate(os.path.join(path,audiofile), False)
"""