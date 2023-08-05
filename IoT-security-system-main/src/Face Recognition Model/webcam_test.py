from model import FaceRecognition
import requests
import cv2 as cv
import numpy as np

train_path = "C:/Users/dinhq/Desktop/IoT-security-system-main/src/Face Recognition Model/train/"

recognizer = FaceRecognition()
trainX, trainY = recognizer.LoadDataset(train_path)
recognizer.fit(trainX, trainY)

print("-------------CAMERA PREPARED----------------")

video = cv.VideoCapture(0)
# video = "http://192.168.0.151"
while True:
    # take image from esp32 cam'
    isTrue,frame = video.read()
    # response = requests.get(url)
    # if response.status_code == 200:
    #     img_array = np.array(bytearray(response.content),dtype=np.uint8)
    #     frame = cv.imdecode(img_array,-1)
    faces = recognizer.detector.detect_faces(frame)
    try:
        
        x, y, w, h = faces[0]["box"]
        face = frame[y-10:y+h+10, x-10:x+w+10]
        name, prob = recognizer.recognition(face)
        if prob < 0.5:
            name = "UNKNOWN"
            
        cv.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),thickness=2)
        cv.putText(frame,name,(x,y-20),cv.FONT_HERSHEY_COMPLEX,1.0,(0,255,0),2)
    except:
        continue
    cv.imshow("Recognizer",frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv.destroyAllWindows()
