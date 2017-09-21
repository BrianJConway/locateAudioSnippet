import numpy as np
import scipy.optimize as op
import os
import locateAudio

# Maps values from 0 to 1
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Normalizes values so that the mean is 0
def normalize(x):
    # Store means of each column in a row vector
    mu = np.mean(x, axis=0)

    # Store std dev of each column in a row vector
    sigma = np.std(x, axis=0)

    # normalize based on mean and std dev of each column
    return (x - mu) / sigma


def costFunctionReg(theta, X, y, lambd):
    # Number of training examples
    m = y.shape[0]

    theta = theta.reshape((X.shape[1], 1))
    y = y.reshape((m, 1))

    # Calculate predicted hypothesis values on training set X with parameters
    # theta
    hyp = sigmoid(X.dot(theta))

    # Calculate unregularized cost value
    yZeroTerm = np.log(hyp).reshape((m, 1))
    yOneTerm = np.log(1 - hyp).reshape((m, 1))

    unregCost = (1 / m) * np.sum(-y * yZeroTerm - (1 - y) * yOneTerm)

    # Set local copy of theta zero to zero
    localTheta = np.array(theta)
    localTheta[0] = 0

    # Calculate sum of squared theta values in a vectorized manner
    sumSquaredTheta = np.dot(localTheta.T, localTheta)

    # Calculate regularization value by scaling the sum of squared thetas
    costRegularization = (lambd / (2 * m)) * sumSquaredTheta
    costRegularization = 0

    J = unregCost + costRegularization

    return J


def gradientsReg(theta, X, y, lambd):
    # Number of training examples
    m = y.shape[0]

    theta = theta.reshape((X.shape[1], 1))
    y = y.reshape((m, 1))

    # Calculate predicted hypothesis values on training set X with parameters
    # theta
    hyp = sigmoid(X.dot(theta))

    # Calculate theta regularization value by scaling thetas
    localTheta = np.array(theta)
    localTheta[0] = 0
    thetaRegularization = (lambd / m) * localTheta

    # Calculate unregularized gradients
    unregGrad = (1 / m) * ((X.T).dot(hyp - y))

    # Calculate regularized gradients
    grad = unregGrad + thetaRegularization

    return grad.flatten()


# Load X and y matrices
dataFile = np.load('data.npz')
X = dataFile['X']
y = np.loadtxt(os.path.join('dataLabels', 'y.txt'))
y = np.reshape(y, (-1, 1))

# Combine and shuffle
all = np.concatenate((X, y), axis=1)
np.random.shuffle(all)

# Separate X and y
X = all[:, 0:5000]
y = all[:, 5000]

# Extract training, test, and cross-validation sets
# Training set is 60% of the dataset
# Test and cross validation sets are each 30% of the dataset
sixtyPercent = int(X.shape[0] * .60)
twentyPercent = int(X.shape[0] * .20)
cValEnd = sixtyPercent + twentyPercent
testEnd = cValEnd + twentyPercent

Xval = X[sixtyPercent:cValEnd, :]
yval = y[sixtyPercent:cValEnd]

Xtest = X[cValEnd:testEnd, :]
ytest = y[cValEnd:testEnd]

X = X[0:sixtyPercent, :]
y = y[0:sixtyPercent]

# Normalize each set
X = normalize(X)
Xval = normalize(Xval)
Xtest = normalize(Xtest)

# Add a column of ones to the front of each set
onesCol = np.array([np.ones(X.shape[0])]).T
X = np.concatenate((onesCol, X), axis=1)

onesCol = np.array([np.ones(Xval.shape[0])]).T
Xval = np.concatenate((onesCol, Xval), axis=1)

onesCol = np.array([np.ones(Xtest.shape[0])]).T
Xtest = np.concatenate((onesCol, Xtest), axis=1)

# Train algorithm on training set
theta = np.zeros(X.shape[1])
lambd = 10

m, n = X.shape
initial_theta = np.zeros(n)
Result = op.minimize(fun=costFunctionReg, x0=theta, args=(
    X, y, lambd), method='TNC', jac=gradientsReg)
optimal_theta = Result.x

# Save learned theta values
np.savez('theta', theta=optimal_theta)
