import mysql.connector
from mysql.connector import Error
import pickle
import random
import k_means as km


try:
    conn = mysql.connector.connect(host = "localhost",
                                    database = "persons",
                                    user = "test",
                                    password = "test")
    
    if conn.is_connected():
        print("Connected to mysql")

        addresses = open("addresses", "r").read().split("\n")
        locations = open("locations", "r").read().split("\n")
        jobs_file = open("jobs", "r").read().split("\n")
        jobs = list()
        for j in jobs_file:
            jobs.append(j.split(":")[0])

        persons = pickle.load(open("faces.p", "rb"))

        mycursor = conn.cursor()

        for person in list(persons):
            
            names =person.split(" ")
            
            firstname_list = names[:-1]
            firstname = ""
            for fn in firstname_list:
                firstname += fn + " "
            firstname = firstname[:-1]
            lastname = names[-1]
            
            if firstname != "George" and lastname != "Husac":
                if (firstname):
                    path_name = firstname + " " + lastname
                else:
                    path_name = lastname
                path_name = path_name.replace(" ", "_")
                img_path = "Resources/faceToAdd/George Husac.jpg"
    

                skin_tone = km.k_means(img_path)
            else:
                skin_tone = "light"

            add = random.choice(addresses)
            loc = random.choice(locations)
            job = random.choice(jobs)
            age = random.randint(18, 60)

            # print(firstname)
            # print(lastname)
            # print(skin_tone)

            sql = "INSERT INTO persons (firstname, lastname, age, skin_tone, job, birth_place, address) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            val = (firstname, lastname, int(age), skin_tone, job, loc, add)

            mycursor.execute(sql, val)
        
        conn.commit()

except Error as e:
    print(e)

    