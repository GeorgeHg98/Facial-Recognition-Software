from xml.dom import NotFoundErr
import cv2
import numpy as np
import k_means as km
import mysql.connector
import pickle
import face_recognition as fr
import onnx
import onnxruntime
from onnx_tf.backend import prepare

class face_recognition():

    MODEL_PATH = "Resources/OnnxFile/ultra_light_640.onnx"

    conn = mysql.connector.connect(host = "localhost",
                                    database = "persons",
                                    user = "test",
                                    password = "test")


    def recognize_feed(self, video_capture):
        onnx_model = onnx.load(self.MODEL_PATH)
        onnx_rt_session = onnxruntime.InferenceSession(self.MODEL_PATH)
        input_name = onnx_rt_session.get_inputs()[0].name

        ret, frame = video_capture.read()
        
        if frame is not None and frame.any():
            height, width, _ = frame.shape

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 480))
            img_mean = np.array([127, 127, 127])
            img = (img - img_mean) / 128
            img = np.transpose(img, [2, 0, 1])
            img = np.expand_dims(img, axis=0)
            img = img.astype(np.float32)

            confidences, boxes = onnx_rt_session.run(None, {input_name: img})
            boxes = self.approximate(width, height, confidences[0], boxes[0], 0.7)

            box = boxes[0]
            
            x1, y1, x2, y2 = box
            frame[0:(y2 - y1), 0:(x2-x1)] = frame[y1:y2, x1:x2]
            cv2.imwrite("sample.jpg", frame[y1-25:y2+25, x1-25:x2+25])

            match = self.searchInDatabase("./sample.jpg")
            if match:
                fname = match.split(" ")[:-1]
                lname = match.split(" ")[-1]

                aux = ""
                for f in fname:
                    aux += f + " "
                fname = aux[:-1]
                print(fname)
                print(lname)
                print(type(match))

                mycursor = self.conn.cursor()

                sql = "SELECT * FROM persons WHERE firstname = '" + fname + "' and lastname = '" + lname + "';"
                print(sql)
                mycursor.execute(sql)
                res = mycursor.fetchall()

                age = res[0][3]
                occupation = res[0][5]
                address = res[0][7]
                born = res[0][6]

                


    def approximate(self, width, height, confidences, boxes, probability_th):
        chosen_boxes_prob = list()

        for index in range(1, confidences.shape[1]):
            probabilities = confidences[:, index]
            mask = probabilities > probability_th
            probabilities = probabilities[mask]

            if probabilities.shape[0] != 0:
                mini_boxes = boxes[mask, :]
                box_prob = np.concatenate([mini_boxes, probabilities.reshape(-1, 1)], axis=1)
                chosen_boxes_prob.append(self.hard_nms(box_prob))

        if chosen_boxes_prob:
            chosen_boxes_prob = np.concatenate(chosen_boxes_prob)
            chosen_boxes_prob[:, 0] *= width
            chosen_boxes_prob[:, 1] *= height
            chosen_boxes_prob[:, 2] *= width
            chosen_boxes_prob[:, 3] *= height
            return chosen_boxes_prob[:, :4].astype(np.int32)

        return np.array([])

    def searchInDatabase(self, img_path):
        skin_tone = km.k_means(img_path)
        print(skin_tone)

        persons = pickle.load(open("faces.p", "rb"))

        if self.conn.is_connected():
            try:
                mycursor = self.conn.cursor()

                sql = "SELECT firstname, lastname FROM persons WHERE skin_tone = '" + skin_tone + "';"

                mycursor.execute(sql)

                results = mycursor.fetchall()
                target_image = fr.load_image_file(img_path)
                target_encoding = fr.face_encodings(target_image)[0]
                persons_keys = list(persons.keys())
                persons_encodings = list(persons.values())
                res = fr.compare_faces(persons_encodings, target_encoding, 0.53)            

                for r in res:
                    if r:
                        index = res.index(r)
                        return(persons_keys[index])
            except:
                return False
            
        return False








