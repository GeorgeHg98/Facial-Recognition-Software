       
import cv2
import numpy
import pickle
import face_recognition

def login():
        resultedName = s.recognize_feed(video_capture= cv2.VideoCapture(0))

        return validate(resultedName)


def validate(name):
        if resultedName == "George Husac":
            return True
        return False 

s = face_recognition()
resultedName = s.recognize_feed(video_capture= cv2.VideoCapture(0))