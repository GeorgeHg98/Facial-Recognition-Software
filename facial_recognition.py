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


class facial_recognition():

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
        
        cv2.imwrite("sample1.jpg", frame)
        
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

            # print(match)

            if match:
                fname = match.split(" ")[:-1]
                lname = match.split(" ")[-1]

                aux = ""
                for f in fname:
                    aux += f + " "
                fname = aux[:-1]
                print(fname)
                print(lname)
                # print(type(match))

                mycursor = self.conn.cursor()

                sql = "SELECT * FROM persons WHERE firstname = '" + fname + "' and lastname = '" + lname + "';"
                
                mycursor.execute(sql)
                res = mycursor.fetchall()
                # print(match)
                return match





    def hard_nms(self, box_probs):
        overlap_thresh = 0.3

        if len(box_probs) == 0:
            return list()

        picked = list()

        x1 = box_probs[:, 0]
        x2 = box_probs[:, 1]
        y1 = box_probs[:, 2]
        y2 = box_probs[:, 3]

        area = (x2 - x1) * (y2 - y1)
        indexes = np.argsort(y2)
        while len(indexes) > 0:
            last_index = indexes[-1]
            picked.append(last_index)
            last_index_index = len(indexes) - 1
            ignore = [last_index_index]

            for pos in range(0, last_index_index):
                current_index = indexes[pos]

                max_x1 = max(x1[last_index], x1[current_index])
                max_y1 = max(y1[last_index], y1[current_index])
                min_x2 = min(x2[last_index], x2[current_index])
                min_y2 = min(y2[last_index], y2[current_index])

                width = max(0, min_x2 - max_x1)
                height = max(0, min_y2 - max_y1)

                overlap = float(width * height) / area[current_index]

                if overlap > overlap_thresh:
                    ignore.append(pos)
            indexes = np.delete(indexes, ignore)
        return box_probs[picked, :]


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
                x = list(persons['George Husac'])
                
                res = fr.compare_faces(persons_encodings, target_encoding, 0.3)   
                print (res)
                for r in res:
                    if r:
                        index = res.index(r)
                        r = False
                for r in res:
                    if r:
                        index = res.index(r)
                        return(persons_keys[index])
            except Exception as ex:
                print(ex)
                return False
            
        return False








