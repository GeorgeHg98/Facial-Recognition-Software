import pickle
import os
import face_recognition as fr

RESOURCE_PATH = 'Resources/faceToAdd/'

name = [x[2] for x in os.walk(RESOURCE_PATH)][0][0]

person_image = fr.load_image_file(RESOURCE_PATH + name)
person_encoding = fr.face_encodings(person_image)[0]

print (name)

persons = pickle.load(open("faces.p", "rb"))

persons[name.split('.')[0]] = person_encoding 

pickle.dump(persons,open('faces.p','wb'))

print (persons)