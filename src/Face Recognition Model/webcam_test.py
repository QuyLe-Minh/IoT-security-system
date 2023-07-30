from model import FaceRecognition
import cv2 as cv

train_path = "C:/Users/Admin/OneDrive - hcmut.edu.vn/powerfulFaceRecognition/train/"

recognizer = FaceRecognition()
trainX, trainY = recognizer.LoadDataset(train_path)
recognizer.fit(trainX, trainY)

print("-------------CAMERA PREPARED----------------")

video = cv.VideoCapture(0)

while True:
    isTrue,frame = video.read()
    faces = recognizer.detector.detect_faces(frame)
    
    for i in range(len(faces)):
        x, y, w, h = faces[i]["box"]
        face = frame[y-10:y+h+10, x-10:x+w+10]
        name, prob = recognizer.recognition(face)
        if prob < 0.5:
            name = "UNKNOWN"
        
        cv.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),thickness=2)
        cv.putText(frame,name,(x,y-20),cv.FONT_HERSHEY_COMPLEX,1.0,(0,255,0),2)

    cv.imshow("Recognizer",frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv.destroyAllWindows()
