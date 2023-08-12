import cv2 as cv
import numpy as np
import requests
import threading
import joblib
from model import FaceRecognition
from keras_facenet import FaceNet
from paho.mqtt import client as mqtt_client
import os

#load model
model_load_path = 'face_recognition_model.pkl'
loaded_recognizer = FaceRecognition()
loaded_recognizer.load_model(model_load_path)

#output folder to save frame
output_dir = "frame_output"
face_dir = "face_output"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(face_dir, exist_ok=True)

# Global variables and locks for thread synchronization
counter=[0,0,0,0]

video = cv.VideoCapture(0)
def fetch_frames_from_camera():
    for i in range(0,5):
        isTrue,frame = video.read()
        if not isTrue: break
        frame_filename = os.path.join(output_dir, f'frame_{i:04d}.jpg')
        cv.imwrite(frame_filename, frame)
    video.release()

def display_frames():
    count = 0
    frame_files = sorted(os.listdir(output_dir))
    for frame_file in frame_files:
        frame_path = os.path.join(output_dir, frame_file)
        frame = cv.imread(frame_path)
        faces = loaded_recognizer.detector.detect_faces(frame)
        
        if len(faces) > 0:
            x, y, w, h = faces[0]["box"]
            face = frame[y-10:y+h+10, x-10:x+w+10]
            name, prob = loaded_recognizer.recognition(face)
            if prob < 0.5:
                name = "UNKNOWN"
        
            cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), thickness=2)
            cv.putText(frame, name, (x, y-20), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0), 2)
        else:
            print("No faces detected in the current frame.")
        
        cv.imshow("Recognizer", frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

#-----------mqtt protocol----------------#

#broker config
broker = 'broker.hivemq.com'
port = 1883
topic_send = "to-esp8266"
topic_receive = "detect-signal"
client_id = "quandinh10"
counter = [0,0,0,0]
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
def publish(client):
    global counter
    client.publish(topic_send,"open")
    counter = [0,0,0,0]

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if (msg.payload.decode("utf-8") == "detect"):
            fetch_frames_from_camera()
            display_frames()
        elif (msg.payload.decode("utf-8") == "quit"):
            client.loop_stop()

    client.subscribe(topic_receive)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()








