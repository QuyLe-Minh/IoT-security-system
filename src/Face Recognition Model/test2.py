import cv2 as cv
import numpy as np
from model import FaceRecognition
from keras_facenet import FaceNet
from paho.mqtt import client as mqtt_client
import os
import threading
from Adafruit_IO import Client, MQTTClient
from connect import *
#load model
model_load_path = 'face_recognition_model.pkl'
loaded_recognizer = FaceRecognition()
loaded_recognizer.load_model(model_load_path)
# Global variables and locks for thread synchronization


def display_frames(client: mqtt_client):
    video = cv.VideoCapture(0)
    for i in range(0,5):
        isTrue,frame = video.read()
        if not isTrue: break

        faces = loaded_recognizer.detector.detect_faces(frame)
        try:
            x, y, w, h = faces[0]["box"]
            face = frame[y-10:y+h+10, x-10:x+w+10]
            name, prob = loaded_recognizer.recognition(face)
            if prob < 0.3:
                name = "UNKNOWN"
            else:
                client.publish("to-esp8266","open")
            cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), thickness=2)
            cv.putText(frame, name, (x, y-20), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0), 2)
        except:
            continue
        cv.imshow("Recognizer", frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        cv.destroyAllWindows()
        video.release()
#-----------mqtt protocol----------------#

    
def connect():
    aio = Client(AIO_USERNAME, AIO_KEY)
    client = MQTTClient(AIO_USERNAME, AIO_KEY)
    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.on_subscribe = subscribe

    client.connect()
    client.loop_background()        
    while True:
        signal_val = aio.receive('detect_signal').value
        if int(signal_val) == 1:
            display_frames()
        else: continue

def main():
    connect()


if __name__ == "__main__":
    main()