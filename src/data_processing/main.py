import os

from keras.preprocessing.image import load_img, img_to_array
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Conv2D, Conv2DTranspose, MaxPooling2D,UpSampling2D
from sklearn.model_selection import train_test_split
import numpy as np
import keras
import matplotlib.pyplot as plt
from PIL import Image
import cv2

def load_data(data_dir):
    def load_images_from_path(path):
        images = []
        for filename in os.listdir(path)[:-1]:
            img_path = os.path.join(path, filename)
            # img = load_img(img_path, color_mode="rgb", grayscale=False)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            img = cv2.equalizeHist(img)
            img = img/255.
            # img = rgb2gray(img)
            # img = np.array(img)
            images.append(img)
        return images

    images = load_images_from_path(data_dir)
    dataset = np.array([np.dstack((images[i], images[i+1], images[i+2])) for i in range(len(images)-2)])

    return dataset

def rgb2gray(rgb):
        """
        Converts an RGB image to grayscale
        """
        return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def prepare_data(images):
    X = images.copy()
    y = to_categorical(np.arange(images.shape[0]))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    return X_train, X_test, y_train, y_test

def merge_datasets(ds1, ds2):
    """
    Merges 2 datasets with same shape to create a one big dataset
    """
    return np.vstack((ds1, ds2))


class Autoencoder():
    def __init__(self):

        self.encoder = Sequential([

            # keras.Input(shape=(120,160, 3)),

            Conv2D(32, (4, 4), strides=2, activation='relu', padding='same', name="enc_conv1"),
            Conv2D(64, (4,4), strides=2, activation='relu', padding='same', name="enc_conv2"),
            Conv2D(128, (4, 4), strides=2, activation='relu', padding='same', name="enc_conv3"),
            # Conv2D(256, (4, 4), strides=2, activation='relu', padding='same', name="enc_conv4")
        ])


        self.decoder = Sequential([
            Conv2DTranspose(128, (4, 4), strides=2, activation='relu', padding='same', name="dec_conv3"),
            Conv2DTranspose(64, (4,4), strides=2, activation='relu', padding='same', name="dec_conv2"),
            Conv2DTranspose(32, (4, 4), strides=2, activation='relu', padding='same', name="dec_conv1")
            # Conv2D(1, (4, 4), activation='sigmoid', padding='same', name="dec_conv4")
            # keras.layer    
            ])

    def build(self):
        return keras.models.Sequential([self.encoder, self.decoder])

if __name__ == '__main__':
    #* we have 2 folders with images
    data_dir1 = '/home/o/Documents/donkeycar_rl/data/images'
    data_dir2 = '/home/o/Documents/donkeycar_rl/data/images2'
    images1 = load_data(data_dir1)
    images2 = load_data(data_dir2)
    images = merge_datasets(images1, images2)

    X_train, X_test, y_train, y_test = prepare_data(images)
    # x_train = np.array(X_train)
    # x_test = np.array(X_test)

    # autoencoder = Autoencoder()
    # autoencoder = autoencoder.build()

    # autoencoder.compile(optimizer='adam', loss=keras.losses.MeanSquaredError())

    # autoencoder.fit(X_train, X_train,
    #                 epochs=10,
    #                 batch_size=32,
    #                 shuffle=True,
    #                 validation_data=(X_test, X_test))

    input_img = keras.Input(shape=(120, 160, 3))
    x = Conv2D(32, (4,4), activation='relu', padding='same')(input_img)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(64, (4,4), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(128, (4,4), activation='relu', padding='same')(x)
    encoded = MaxPooling2D((2, 2), padding='same')(x)

    # Define the Decoder
    x = Conv2D(128, (4,4), activation='relu', padding='same')(encoded)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(64, (4,4), activation='relu', padding='same')(x)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(32, (4,4), activation='relu', padding='same')(x)
    x = UpSampling2D((2, 2))(x)
    decoded = Conv2D(3, (4,4), activation='sigmoid', padding='same')(x)

    # Combine Encoder and Decoder
    autoencoder = keras.Model(input_img, decoded)

    # Compile the Model
    autoencoder.compile(optimizer='adam', loss='mse')   

    autoencoder.fit(X_train, X_train,
                epochs=20,
                batch_size=64,
                shuffle=True,
                validation_data=(X_test, X_test))
 
    #compare same image as input and output of decoder
    test_samples = [0, 600, 300, 1000]
    preds = [autoencoder.predict(np.expand_dims(X_test[i], axis=0)) for i in test_samples]
    img1, img2, img3, img4 = [X_test[i] for i in test_samples]
    pred1, pred2, pred3, pred4 = preds

    fig, ax = plt.subplots(4, 2)
    ax[0, 0].imshow(img1)
    ax[0, 1].imshow(pred1[0])

    ax[1, 0].imshow(img2)
    ax[1, 1].imshow(pred2[0])

    ax[2, 0].imshow(img3)
    ax[2, 1].imshow(pred3[0])

    ax[3, 0].imshow(img4)
    ax[3, 1].imshow(pred4[0])

    plt.show()

