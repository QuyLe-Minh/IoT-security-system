import cv2 as cv
import numpy as np
from model import FaceRecognition
from keras_facenet import FaceNet
from paho.mqtt import client as mqtt_client
import os
import threading


#load model
model_load_path = 'face_recognition_model.pkl'
loaded_recognizer = FaceRecognition()
loaded_recognizer.load_model(model_load_path)
# Global variables and locks for thread synchronization
exit_event = threading.Event()
detect_event = threading.Event()


def display_frames(client: mqtt_client):
    while (not exit_event.is_set()):
        if detect_event.is_set():
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
        detect_event.clear()
        cv.destroyAllWindows()
        video.release()
        continue
#-----------mqtt protocol----------------#

#broker config
broker = 'broker.hivemq.com'
port = 1883
topic_send = "to-esp8266"
topic_receive = "detect-signal"
client_id = "quandinh10"
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

def on_message(client,userdata,msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if (msg.payload.decode("utf-8") == "detect"):
            detect_event.set()
        elif (msg.payload.decode("utf-8") == "quit"):
            exit_event.set()
    

        
client = connect_mqtt()
client.subscribe(topic_receive)
client.on_message = on_message
client.loop_background()
recognition_thread = threading.Thread(target=display_frames, args=(client,))


recognition_thread.start()
    
recognition_thread.join()

client.disconnect()
client.loop_stop()