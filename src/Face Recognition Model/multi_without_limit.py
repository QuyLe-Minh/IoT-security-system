import cv2 as cv
import numpy as np
import requests
import threading
from model import FaceRecognition
from paho.mqtt import client as mqtt_client


train_path = "C:/Users/dinhq/Desktop/IoT-security-system-main/src/Face Recognition Model/train/"

recognizer = FaceRecognition()
trainX, trainY = recognizer.LoadDataset(train_path)
recognizer.fit(trainX, trainY)


# Global variables and locks for thread synchronization
frame = None
faces = None
exit_event = threading.Event()
frame_lock = threading.Lock()
faces_lock = threading.Lock()

#-----------mqtt protocol----------------#

#broker config
broker = 'broker.hivemq.com'
port = 1883
topic = "to-esp8266"
client_id = "quandinh10"
counter = [0,0,0,0]
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

client = connect_mqtt()
client.loop_start()

def publish(client):
    global counter
    client.publish(topic,"open")
    counter = [0,0,0,0]


# Define the interval for face detection (perform detection every n frames)
# video = "http://192.168.1.9/cam-lo.jpg"
video = cv.VideoCapture(0)
def fetch_frames_from_camera():
    global frame
    while not exit_event.is_set():
        isTrue,frame = video.read()
        if not isTrue:
            continue
        # response = requests.get(video)
        # if response.status_code == 200:
        #     img_array = np.array(bytearray(response.content),dtype=np.uint8)
        #     frame = cv.imdecode(img_array,-1)

def process_frames():
    global frame, faces
    while not exit_event.is_set():
        if frame is not None:
            # Perform face detection on the fetched frame every n frames
            with frame_lock:
                faces = recognizer.detector.detect_faces(frame)

    cv.destroyAllWindows()

def display_frames():
    global frame, faces

    while not exit_event.is_set():
        if frame is not None:
            # Draw face rectangles and labels on the display_frame
            with faces_lock:
                if faces is not None:
                    try:
                        for face_info in faces:
                            x, y, w, h = face_info["box"]
                            face = frame[y-10:y+h+10, x-10:x+w+10]
                            name, prob = recognizer.recognition(face)

                            if prob < 0.5:
                                name = "UNKNOWN"
                            else:
                                if (name=="Nhan"):
                                    counter[0]+=1
                                    if (counter[0]==5):
                                        publish(client)
                                elif (name=="Quan"):
                                    counter[1]+=1
                                    if (counter[1]==5):
                                        publish(client)
                                elif (name=="Quy"):
                                    counter[2]+=1
                                    if (counter[2]==5):
                                        publish(client)
                                else:
                                    counter[3]+=1
                                    if (counter[3]==5):
                                        publish(client)
                            cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), thickness=2)
                            cv.putText(frame, name, (x, y-20), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0), 2)

                    except Exception as e:
                        print("Error:", e)
            cv.imshow("Recognizer", frame)

        # Check for 'q' key press to exit the program
        if cv.waitKey(1) & 0xFF == ord('q'):
            exit_event.set()
            client.loop_stop()

    cv.destroyAllWindows()

# Create and start the threads
fetch_thread = threading.Thread(target=fetch_frames_from_camera)
process_thread = threading.Thread(target=process_frames)
display_thread = threading.Thread(target=display_frames)


fetch_thread.start()
process_thread.start()
display_thread.start()


# Wait for the threads to finish
fetch_thread.join()
process_thread.join()
display_thread.join()