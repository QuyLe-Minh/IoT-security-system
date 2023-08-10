import cv2 as cv
import numpy as np
import requests
import threading
import joblib
from model import FaceRecognition
from keras_facenet import FaceNet

model_load_path = 'face_recognition_model.pkl'
loaded_recognizer = FaceRecognition()

loaded_recognizer.load_model(model_load_path)

# Global variables and locks for thread synchronization
frame = None
faces = None
exit_event = threading.Event()
frame_lock = threading.Lock()
faces_lock = threading.Lock()

# Define the interval for face detection (perform detection every n frames)
video = "http://192.168.1.10/cam-lo.jpg"
def fetch_frames_from_camera():
    global frame
    while not exit_event.is_set():
        response = requests.get(video)
        if response.status_code == 200:
            img_array = np.array(bytearray(response.content),dtype=np.uint8)
            frame = cv.imdecode(img_array,-1)

def process_frames():
    global frame, faces
    while not exit_event.is_set():
        if frame is not None:
            # Perform face detection on the fetched frame every n frames
            with frame_lock:
                faces = loaded_recognizer.detector.detect_faces(frame)

    cv.destroyAllWindows()

def display_frames():
    global frame, faces

    while not exit_event.is_set():
        if frame is not None:
            display_frame = frame.copy()
            # Draw face rectangles and labels on the display_frame
            with faces_lock:
                if faces is not None:
                    try:
                        for face_info in faces:
                            x, y, w, h = face_info["box"]
                            face = frame[y-10:y+h+10, x-10:x+w+10]
                            name, prob = loaded_recognizer.recognition(face)

                            if prob < 0.5:
                                name = "UNKNOWN"

                            cv.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), thickness=2)
                            cv.putText(display_frame, name, (x, y-20), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0), 2)

                    except Exception as e:
                        print("Error:", e)
            display_frame = cv.resize(display_frame, (400,400))
            cv.imshow("Recognizer", display_frame)

        # Check for 'q' key press to exit the program
        if cv.waitKey(1) & 0xFF == ord('q'):
            exit_event.set()

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
