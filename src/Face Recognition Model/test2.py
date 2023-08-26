import cv2 as cv
import numpy as np
from model import FaceRecognition
from keras_facenet import FaceNet
from paho.mqtt import client as mqtt_client
from Adafruit_IO import Client, MQTTClient
from connect import *
# import threading
import time
#load model
model_load_path = 'face_recognition_model.pkl'
loaded_recognizer = FaceRecognition()
loaded_recognizer.load_model(model_load_path)
# Global variables and locks for thread synchronization


def display_frames(aio: Client):
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
                aio.send_data("face-recognize","open")
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
        data = aio.receive('detect-signal').value
        if (int(data)==1):
            print("detect")
            display_frames(aio)
            # check=False
        # check_sync.release()
        # time.sleep(1)



if __name__ == "__main__":
    connect()