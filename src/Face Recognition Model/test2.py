import cv2 as cv
import numpy as np
from model import FaceRecognition
from keras_facenet import FaceNet
from paho.mqtt import client as mqtt_client
from Adafruit_IO import Client, MQTTClient
from connect import *
from face_recognize_db import * 
# import threading
import time
#load model
model_load_path = 'face_recognition_model.pkl'
loaded_recognizer = FaceRecognition()
loaded_recognizer.load_model(model_load_path)
# Global variables and locks for thread synchronization


def display_frames(aio: Client):
    video = cv.VideoCapture(0)
    isTrue,frame = video.read()
    if not isTrue: return
    faces = loaded_recognizer.detector.detect_faces(frame)
    try:
        x, y, w, h = faces[0]["box"]
        face = frame[y-10:y+h+10, x-10:x+w+10]
        name, prob = loaded_recognizer.recognition(face)
        if prob < 0.3:
            name="Stranger"            
        aio.send_data("face-recognize",name)
        collection.insert_one({"Date": datetime.now(), "Name": name})
    except:
        aio.send_data("face-recognize","Stranger")
        collection.insert_one({"Date": datetime.now(), "Name": "Stranger"})
        return
    
    cv.destroyAllWindows()
    video.release()
#-----------mqtt protocol----------------#

    
def connect():
    # global check
    aio = Client(AIO_USERNAME,AIO_KEY)
    client = MQTTClient(AIO_USERNAME, AIO_KEY)
    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.on_subscribe = subscribe

    client.connect()
    client.loop_background()        
    while True:
        # check_sync.acquire()
        try:
            data = aio.receive_next('detect-signal').value
        except:
            continue
        display_frames(aio)
            # check=False
        # check_sync.release()
        # time.sleep(1)
        


if __name__ == "__main__":
    connect()