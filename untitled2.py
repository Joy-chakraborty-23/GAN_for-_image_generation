# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yHxGkHHFHfNP95XJGqlah1ssaU1vmY-2
"""

from google.colab import drive
drive.mount('/content/drive')

import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import os
from glob import glob
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Set parameters
IMG_HEIGHT = 512
IMG_WIDTH = 512
CHANNELS = 3
NOISE_DIM = 100
BATCH_SIZE = 64
EPOCHS = 50000
SAVE_INTERVAL = 1000

# Preprocessing function
def preprocess_images(image_folder):
    image_paths = glob(os.path.join(image_folder, "*.jpg"))  # Adjust extension as needed
    images = []
    for img_path in image_paths:
        img = load_img(img_path, target_size=(IMG_HEIGHT, IMG_WIDTH))
        img = img_to_array(img) / 255.0  # Normalize to [0, 1]
        images.append(img)
    return np.array(images)

# Load dataset
# Load dataset
def load_data(data_folder):
    images = preprocess_images(data_folder)
    if images.size == 0:
        raise ValueError(f"No images found in the folder: {data_folder}. Check the path and image formats.")
    return images


# Generator
def build_generator():
    model = tf.keras.Sequential([
        layers.Dense(64 * 64* 256, input_dim=NOISE_DIM),
        layers.Reshape((64,64, 256)),
        layers.Conv2DTranspose(128, kernel_size=4, strides=2, padding="same", activation="relu"),
        layers.Conv2DTranspose(64, kernel_size=4, strides=2, padding="same", activation="relu"),
        layers.Conv2DTranspose(CHANNELS, kernel_size=4, strides=2, padding="same", activation="sigmoid")
    ])
    return model

# Discriminator
def build_discriminator():
    model = tf.keras.Sequential([
        layers.Conv2D(64, kernel_size=4, strides=2, padding="same", input_shape=(IMG_HEIGHT, IMG_WIDTH, CHANNELS)),
        layers.LeakyReLU(alpha=0.2),
        layers.Conv2D(128, kernel_size=4, strides=2, padding="same"),
        layers.LeakyReLU(alpha=0.2),
        layers.Flatten(),
        layers.Dense(1, activation="sigmoid")
    ])
    return model

# GAN Model
def build_gan(generator, discriminator):
    discriminator.trainable = False
    model = tf.keras.Sequential([generator, discriminator])
    return model

# Compile models
generator = build_generator()
discriminator = build_discriminator()
discriminator.compile(optimizer=tf.keras.optimizers.Adam(0.0002, 0.5), loss="binary_crossentropy", metrics=["accuracy"])
gan = build_gan(generator, discriminator)
gan.compile(optimizer=tf.keras.optimizers.Adam(0.0002, 0.5), loss="binary_crossentropy")

# Training function
def train_gan(dataset):
    real_labels = np.ones((BATCH_SIZE, 1))
    fake_labels = np.zeros((BATCH_SIZE, 1))

    for epoch in range(EPOCHS):
        # Train discriminator
        idx = np.random.randint(0, dataset.shape[0], BATCH_SIZE)
        real_images = dataset[idx]
        noise = np.random.normal(0, 1, (BATCH_SIZE, NOISE_DIM))
        fake_images = generator.predict(noise)

        d_loss_real = discriminator.train_on_batch(real_images, real_labels)
        d_loss_fake = discriminator.train_on_batch(fake_images, fake_labels)

        # Extract scalar values correctly from the losses
        d_loss_real_value, d_acc_real = d_loss_real[0], d_loss_real[1]
        d_loss_fake_value, d_acc_fake = d_loss_fake[0], d_loss_fake[1]

        # Average the loss and accuracy
        d_loss = 0.5 * (d_loss_real_value + d_loss_fake_value)
        d_acc = 0.5 * (d_acc_real + d_acc_fake)

        # Train generator
        noise = np.random.normal(0, 1, (BATCH_SIZE, NOISE_DIM))
        g_loss = gan.train_on_batch(noise, real_labels)  # Extract scalar value from the result
        if isinstance(g_loss, (list, tuple)):
            g_loss = g_loss[0]

        # Output progress
        if epoch % SAVE_INTERVAL == 0:
            print(f"Epoch {epoch}, D Loss: {d_loss:.4f}, D Acc: {d_acc:.4f}, G Loss: {g_loss:.4f}")
            save_images(epoch, generator)

# Save generated images
def save_images(epoch, generator, folder="generated_images"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    noise = np.random.normal(0, 1, (16, NOISE_DIM))
    gen_images = generator.predict(noise)
    gen_images = (gen_images * 255).astype(np.uint8)

    for i, img in enumerate(gen_images):
        tf.keras.preprocessing.image.save_img(os.path.join(folder, f"image_{epoch}_{i}.png"), img)

# Main execution
# Main execution
data_folder = "/content/drive/MyDrive/img data purnima Gan"  # Replace with the correct path to your image folder
dataset = load_data(data_folder)

print(f"Loaded {dataset.shape[0]} images from the dataset.")  # Debugging step
train_gan(dataset)