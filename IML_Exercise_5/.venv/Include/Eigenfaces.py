import numpy as np
import cv2
import matplotlib.pyplot as plt

from sklearn.svm import SVC

# image size
N = 64

# Define the classifier in clf - Try a Support Vector Machine with C = 0.025 and a linear kernel
# DON'T change this!
clf = SVC(kernel="linear", C=0.025)


def create_database_from_folder(path):
    '''
    DON'T CHANGE THIS METHOD.
    If you run the Online Detection, this function will load and reshape the
    images located in the folder. You pass the path of the images and the function returns the labels,
    training data and number of images in the database
    :param path: path of the training images
    :return: labels, training images, number of images
    '''
    labels = list()
    filenames = np.sort(path)
    num_images = len(filenames)
    train = np.zeros((N * N, num_images))
    for n in range(num_images):
        img = cv2.imread(filenames[n], cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (N, N))
        assert img.shape == (N, N), 'Image {0} of wrong size'.format(filenames[n])
        train[:, n] = img.reshape((N * N))
        labels.append(filenames[n].split("eigenfaces/")[1].split("_")[0])
    print('Database contains {0} images'.format(num_images))
    labels = np.asarray(labels)
    return labels, train, num_images


def process_and_train(labels, train, num_images, h, w):
    '''
    Calculate the essentials: the average face image and the eigenfaces.
    Train the classifier on the eigenfaces and the given training labels.
    :param labels: 1D-array
    :param train: training face images, 2D-array with images as row vectors (e.g. 64x64 image ->  4096 vector)
    :param num_images: number of images, int
    :param h: height of an image
    :param w: width of an image
    :return: the eigenfaces as row vectors (2D-array), number of eigenfaces, the average face
    '''
    avg_face = calculate_average_face(train)
    print(" P&T > H,W: {0},{1}".format(h,w))
    num_eigenfaces = min(num_images - 1, h * w)
    eigenfaces = calculate_eigenfaces(train, avg_face, num_eigenfaces)
    features = get_feature_representation(train.T, eigenfaces, avg_face, num_eigenfaces)

    clf.fit(features, labels)

    return eigenfaces, num_eigenfaces, avg_face


def calculate_average_face(train):
    '''
    Calculate the average face using all training face images
    :param train: training face images, 2D-array with images as row vectors
    :return: average face, 1D-array shape(#pixels)
    '''
    return np.mean(train, axis=0)


def calculate_eigenfaces(train, avg, num_eigenfaces):
    '''
    Calculate the eigenfaces from the given training set using SVD
    :param train: training face images, 2D-array with images as row vectors
    :param avg: average face, 1D-array
    :param num_eigenfaces: number of eigenfaces to return from the computed SVD
    :return: the eigenfaces as row vectors, 2D-array --> shape(num_eigenfaces, #pixel of an image)
    '''
    train = train[0:num_eigenfaces, :]
    X = train - avg

    u, s, v = np.linalg.svd(X)
    print("shape of u", u.shape)
    print('Size of u: {0} x {1}'.format(len(u), len(u[0])))
    print('Size of s: {0}'.format(len(s)))
    print('Size of v: {0} x {1}'.format(len(v), len(v[0])))
    S = np.zeros((len(u), len(v)), dtype=float)
    S[:len(s), :len(s)] = np.diag(s)
    print(np.allclose(X, np.dot(u, np.dot(S, v))))
    print(np.allclose(np.dot(u, u.T), len(u)))
    #hello how are you
    return u

def get_feature_representation(images, eigenfaces, avg, num_eigenfaces):
    '''
    For all images, compute their eigenface-coefficients with respect to the given amount of eigenfaces
    :param images: 2D-matrix with a set of images as row vectors, shape (#images, #pixels)
    :param eigenfaces: 2D-array with eigenfaces as row vectors, shape(#pixels, #pixels)
                       -> only use the given number of eigenfaces
    :param avg: average face, 1D-array
    :param num_eigenfaces: number of eigenfaces to compute coefficients for
    :return: coefficients/features of all training images, 2D-matrix (#images, #used eigenfaces)
    '''
    X = images - avg
    features = np.dot(X, eigenfaces.T)
    return features


def reconstruct_image(img, eigenfaces, avg, num_eigenfaces, h, w):
    '''
    Reconstruct the given image by weighting the eigenfaces according to their coefficients
    :param img: input image to be reconstructed, 1D array
    :param eigenfaces: 2D array with all available eigenfaces as row vectors
    :param avg: the average face image, 1D array
    :param num_eigenfaces: number of eigenfaces used to reconstruct the input image
    :param h: height of a original image
    :param w: width of a original image
    :return: the reconstructed image, 2D array (shape of a original image)
    '''
    img_zero_mean = img - avg
    coeffs = np.dot(img_zero_mean, eigenfaces[:num_eigenfaces].T)
    reconstruction = avg + np.dot(coeffs, eigenfaces[:num_eigenfaces])
    return reconstruction.reshape(h, w)


def classify_image(img, eigenfaces, avg, num_eigenfaces, h, w):
    '''
    Classify the given input image using the trained classifier
    :param img: input image to be classified, 1D-array
    :param eigenfaces: all given eigenfaces, 2D array with the eigenfaces as row vectors
    :param avg: the average image, 1D array
    :param num_eigenfaces: number of eigenfaces used to extract the features
    :param h: height of a original image
    :param w: width of a original image
    :return: the predicted labels using the classifier, 1D-array (as returned by the classifier)
    '''
    img_zero_mean = img - avg
    features = np.dot(img_zero_mean, eigenfaces[:num_eigenfaces].T)
    return clf.predict([features])
