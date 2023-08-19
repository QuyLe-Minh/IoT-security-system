import cv2 as cv
import numpy as np
from model import FaceRecognition

train_path = "C:/Users/dinhq/Desktop/IoT-security-system-main/src/Face Recognition Model/train/"
# model_save_path = "C:/Users/dinhq/Desktop/IoT-security-system-main/src/Face Recognition Model/"
# Instantiate your FaceRecognition class
recognizer = FaceRecognition()

# Train your model (assumed you've done this already)
trainX, trainY = recognizer.LoadDataset(train_path)
recognizer.fit(trainX, trainY)

# Define a file path to save the trained model
save_model= 'face_recognition_model.pkl'

# Save the trained model
recognizer.save_model(save_model)

print(f"Trained model saved to {save_model}")
