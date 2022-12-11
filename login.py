import cv2
import facial_recognition as fr

recognizer = fr.facial_recognition()

def login():
        resultedName = recognizer.recognize_feed(video_capture= cv2.VideoCapture(0))

        return validate(resultedName)

def validate():
        resultedName = recognizer.recognize_feed(video_capture= cv2.VideoCapture(0))
        print(resultedName)
        if resultedName == "George Husac":
            return (True, resultedName)
        return (False, resultedName) 

valid = validate()

if valid[0] == True:
        print('Welcome to the App ' + valid[1] + '!')

else: print("Unauthorized Access")



