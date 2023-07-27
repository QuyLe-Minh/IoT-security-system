from mtcnn.mtcnn import MTCNN
from PIL import Image
import numpy as np
import os
from collections import defaultdict
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from keras_facenet import FaceNet


class FaceRecognition:
    def __init__(self): 
        self.detector = MTCNN()
        self.model = FaceNet()
        self.__embedding = []
        self.out_encoder = LabelEncoder()           #Transform array(n_examples, embeddings)
        self.in_encoder = Normalizer(norm="l2")     #Transform array(n_examples, labels)
        self.database = defaultdict(list)
        self.minDist = None
        self.maxDist = None
        
    def __ExtractFace(self, fileName, size = (160, 160)):
        """
        Extract a face from given image and resize it to size.
        
        Args:
            filename: directory to image, parse later
            size: desired size
        """
        image = Image.open(fileName)
        image = image.convert("RGB")
        image = np.asarray(image)
        results = self.detector.detect_faces(image)
        x1, y1, width, height = results[0]["box"]
        x1, y1 = abs(x1), abs(y1)
        face = image[y1-20:y1+height+20, x1-20:x1+width+20]
        image = Image.fromarray(face)
        image = image.resize(size)
        face_array = np.asarray(image)
        return face_array
    
    def __LoadFaces(self, directory):
        """
        Load all faces from given person.
        
        Args:
            directory: path to person folder, parse later
        """
        faces = []
        for filename in os.listdir(directory):
            path = directory + filename
            faces.append(self.__ExtractFace(path))
        return faces
    
    def LoadDataset(self, directory):
        """
        Load data from path
        
        Args:
            directory: parse later
        Return:
            X: numpy array of cropped face
            Y: numpy array of labels
        """
        X, Y = [], []
        for subdir in os.listdir(directory):
            path = directory + subdir + '/'
            print(path)
            if not os.path.isdir(path):
                continue
            faces = self.__LoadFaces(path)
            labels = [subdir for _ in range(len(faces))]
            X.extend(faces)
            Y.extend(labels)
        X = np.asarray(X)
        Y = np.asarray(Y)
        return X, Y
            
            
    def add(self, dir):
        """
        Add new person
        
        Args:
            directory: path to person folder, parse later
        """
        for img in os.listdir(dir):
            pass
        
    def remove(self, name):
        self.database.pop(name)
        
    def __Embedding(self, face):
        """
        Get embedding of a face
        
        Args:
            face: numpy array
        
        Return:
            128-d array embedding
        """
        face = np.expand_dims(face, axis = 0)
        yhat = self.model.embeddings(face)
        return yhat[0]
        
    def fit(self, X, Y):
        """
        Fit the classifier
        """
        for face in X:
            embedding = self.__Embedding(face)
            self.__embedding.append(embedding)
        embeddings = np.asarray(self.__embedding)
        embeddings = self.in_encoder.transform(embeddings)       
        self.out_encoder.fit(Y)
        trainY = self.out_encoder.transform(Y)
        
        self.clf.fit(embeddings, trainY)
        print(self.predict(embeddings))
        
    def predict(self, X):
        return self.clf.predict(X)
    
    def evaluate(self, trainX, trainY, testX, testY):
        pred = self.predict(trainX)
        train = np.mean(pred == trainY)
        pred = self.predict(testX)
        val = np.mean(pred == testY)
        print("Accuracy: train=%.3f, test=%.3f" % (train*100, val*100))
        
    def recognition(self, X):
        """
        Args:
            X: extracted face
            
        Return:
            name:
            probability
        """
        X = self.__Embedding(X)
        X = np.expand_dims(X, axis = 0)
        X = self.in_encoder.transform(X)
        yhat_class = self.clf.predict(X)
        yhat_proba = self.clf.predict_proba(X)
        name = self.out_encoder.inverse_transform(yhat_class)
        return name, yhat_proba