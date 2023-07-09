import os
import pickle
import cvzone as cvzone
import numpy as np
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import csv

# initialising the database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(credential=cred, options={
    'databaseURL': "https://faceattendancesystem-ac890-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancesystem-ac890.appspot.com"
})

# Load the known faces and their names
# known_faces = []
# known_names = []
# load the encoding file
print("Loading encode file....")
file = open('EncodingFile.p', "rb")
encodeListKnownWithIDs = pickle.load(file)
encodeListKnown, employeeIDs = encodeListKnownWithIDs
print("Encode file loaded :-D")

# # Load the known faces from images and store their encodings
# image_files = ['123456.png', '987456.png']
# for file in image_files:
#     image = face_recognition.load_image_file(file)
#     encoding = face_recognition.face_encodings(image)[0]
#     known_faces.append(encoding)
#     known_names.append(file.split('.')[0])


# Initialize some variables+
mob_face_locations = []
mob_face_encodings = []
laptop_faces_name = []

# Load the video capture laptop camera
print('loading laptop camera......')
laptop_video_capture = cv2.VideoCapture(0)
print("laptop_camera_loaded.")
# Load the mobile camera
print('loading mobile camera......')
mobile_video_capture = cv2.VideoCapture(1)
address = "http://100.95.54.163:8080/video"
mobile_video_capture.open(address)
print("mobile camera loaded.")

while True:
    # Read a single frame from the video capture
    laptop_ret, laptop_frame = laptop_video_capture.read()
    mob_ret, mob_frame = mobile_video_capture.read()

    # flip the image latterly
    laptop_frame = cv2.flip(laptop_frame, 1)

    # Resize the frame to 1/4 size of the original to improve speed
    small_laptop_frame = cv2.resize(laptop_frame, (0, 0), fx=0.25, fy=0.25)
    small_mob_frame = cv2.resize(mob_frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color to RGB color
    rgb_small_laptop_frame = cv2.cvtColor(small_laptop_frame, cv2.COLOR_BGR2RGB)
    rgb_small_mob_frame = cv2.cvtColor(small_mob_frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and their encodings in the current frame
    print('finding the encoding and their location')
    laptop_face_locations = face_recognition.face_locations(rgb_small_laptop_frame)
    # laptop_face_encodings = face_recognition.face_encodings(rgb_small_laptop_frame, mob_face_locations)
    laptop_face_encodings = face_recognition.face_encodings(rgb_small_laptop_frame)
    #### print("laptop face encodings: ", laptop_face_encodings)
    mob_face_locations = face_recognition.face_locations(rgb_small_mob_frame)
    mob_face_encodings = face_recognition.face_encodings(rgb_small_mob_frame, mob_face_locations)

    # Initialize an empty list to store the names of the detected faces
    laptop_faces_name = []

    # matching faces on laptop screen
    if laptop_face_locations:
        print('matching faces...')
        for face_encoding in laptop_face_encodings:
            # Check if the face matches any known faces
            matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
            name = "Unknown"

            # lower the face distance better the accuracy of the face detect
            faceDistance = face_recognition.face_distance(face_encodings=encodeListKnown,
                                                          face_to_compare=face_encoding)

            # If a match is found, use the known face name
            #### print("matches: ", matches)

            # get the least face-distance valued Index in faceDistance List
            matchIndex = np.argmin(faceDistance)
            #### print("matchIndex : ", matchIndex)

            # check for the matches(face matching list) if the index is correct or not
            print("matches[matchIndex]: ", matches[matchIndex])

            if matches[matchIndex]:
                # get the employee id
                ID = employeeIDs[matchIndex]

                # import the information of employee from the database
                employeeInfo = db.reference(f'Employees/{ID}').get()
                #### print(employeeInfo)

                name = employeeInfo['name']
                print(name)
            # Add the name to the list of face names
            laptop_faces_name.append(name)

        # update the attendance
        ref = db.reference(f'Employees/{ID}')
        datetimeObject = datetime.strptime(employeeInfo['last time attendance'], '%Y-%m-%d %H:%M:%S')
        secondElapsed = (datetime.now() - datetimeObject).total_seconds()
        print('checking the time elapsed..')
        print("secondElapsed: ", secondElapsed)

        if secondElapsed > 30:
            # increase the attendance bu 1
            employeeInfo['total attendance'] += 1
            ref.child('total attendance').set(employeeInfo['total attendance'])
            # updating the last time attendance
            currTime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            ref.child('last time attendance').set(currTime)
            last_time_attendance = currTime

            # updating the entry csv file
            with open('Entry_time.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                data = [[ID, employeeInfo['name'], last_time_attendance]]
                writer.writerows(data)
        else:
            print('your attendance is already done. :)')

    mob_faces_name = []
    # matching faces on mobile screen
    if mob_face_locations:
        for face_encoding in mob_face_encodings:
            # Check if the face matches any known faces
            matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
            name = "Unknown"

            # lower the face distance better the accuracy of the face detect
            faceDistance = face_recognition.face_distance(face_encodings=encodeListKnown,
                                                          face_to_compare=face_encoding)

            # If a match is found, use the known face name
            #### print("matches of mobile:", matches)
            if True in matches:
                # get the least face-distance valued Index in faceDistance List
                matchIndex = np.argmin(faceDistance)
                #### print("matchIndex of mobile : ", matchIndex)

                # get the employee id
                ID = employeeIDs[matchIndex]

                # import the information of employee from the database
                employeeInfo = db.reference(f'Employees/{ID}').get()
                #### print(employeeInfo)

                name = employeeInfo['name']
                print(f'detected mob faces name: {name}')
            # Add the name to the list of face names
            mob_faces_name.append(name)

        # update the attendance
        ref = db.reference(f'Employees/{ID}')
        datetimeObject = datetime.strptime(employeeInfo['last time attendance'], '%Y-%m-%d %H:%M:%S')
        secondElapsed = (datetime.now() - datetimeObject).total_seconds()
        print('checking the time elapsed..')
        print("secondElapsed: ", secondElapsed)

        if secondElapsed > 30:
            # increase the attendance bu 1
            employeeInfo['total attendance'] += 1
            ref.child('total attendance').set(employeeInfo['total attendance'])
            # updating the last time attendance
            currTime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            ref.child('last time attendance').set(currTime)
            last_time_attendance = currTime

            # updating the entry csv file
            with open('Exit_time.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                data = [[ID, employeeInfo['name'], last_time_attendance]]
                writer.writerows(data)
        else:
            print('your exit attendance is already done. :)')

    # Display the results
    print("isssss baar hogya")
    # print('mob_face_locations:  ', mob_face_locations)
    # print("mob_faces_name:  ", mob_faces_name)
    # print('laptop_face_locations:  ', laptop_face_locations)
    # print("laptop_faces_name:  ", laptop_faces_name)

    # for laptop
    for (laptop_top, laptop_right, laptop_bottom, laptop_left), laptop_name in zip(laptop_face_locations,
                                                                                   laptop_faces_name):
        print("exatually hogya")
        # # for top, right, bottom, left in face_locations:
        # Scale the face locations back up since the frame was resized
        # mob_top *= 4
        # mob_right *= 4
        # mob_bottom *= 4
        # mob_left *= 4
        laptop_top *= 4
        laptop_right *= 4
        laptop_bottom *= 4
        laptop_left *= 4

        # Draw a box around the face
        print("drawing the boxes....")
        # for laptop
        cv2.rectangle(laptop_frame, (laptop_left, laptop_top), (laptop_right, laptop_bottom), (0, 0, 255), 2)

        # # for mobile
        # cv2.rectangle(mob_frame, (mob_left, mob_top), (mob_right, mob_bottom), (0, 0, 255), 2)

        # Draw a label with the name below the face
        print('labeling the faces')
        # for laptop
        cv2.rectangle(laptop_frame, (laptop_left, laptop_bottom - 35), (laptop_right, laptop_bottom), (0, 0, 255),
                      cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(laptop_frame, laptop_name, (laptop_left + 6, laptop_bottom - 6), font, 0.8, (255, 255, 255), 1)

        # # for mobile
        # cv2.rectangle(mob_frame, (mob_left, mob_bottom - 35), (mob_right, mob_bottom), (0, 0, 255),
        #               cv2.FILLED)
        # font = cv2.FONT_HERSHEY_DUPLEX
        # cv2.putText(mob_frame, mob_name, (mob_left + 6, mob_bottom - 6), font, 0.8, (255, 255, 255), 1)

    # for mobile
    for (mob_top, mob_right, mob_bottom, mob_left), mob_name in zip(mob_face_locations, mob_faces_name):
        print("exatually hogya")
        # # for top, right, bottom, left in face_locations:
        # Scale the face locations back up since the frame was resized
        mob_top *= 4
        mob_right *= 4
        mob_bottom *= 4
        mob_left *= 4

        # Draw a box around the face
        print("drawing the boxes....")
        # for laptop
        cv2.rectangle(mob_frame, (mob_left, mob_top), (mob_right, mob_bottom), (0, 0, 255), 2)

        # # for mobile
        # cv2.rectangle(mob_frame, (mob_left, mob_top), (mob_right, mob_bottom), (0, 0, 255), 2)

        # Draw a label with the name below the face
        print('labeling the faces')
        # for laptop
        cv2.rectangle(mob_frame, (mob_left, mob_bottom - 35), (mob_right, mob_bottom), (0, 0, 255),
                      cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(mob_frame, mob_name, (mob_left + 6, mob_bottom - 6), font, 0.8, (255, 255, 255), 1)

        # # for mobile
        # cv2.rectangle(mob_frame, (mob_left, mob_bottom - 35), (mob_right, mob_bottom), (0, 0, 255),
        #               cv2.FILLED)
        # font = cv2.FONT_HERSHEY_DUPLEX
        # cv2.putText(mob_frame, mob_name, (mob_left + 6, mob_bottom - 6), font, 0.8, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Laptop_Video_Capture', laptop_frame)
    cv2.imshow('Mobile_Video_Capture', mob_frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and destroy all windows
laptop_video_capture.release()
cv2.destroyAllWindows()

# **************************************************** final code **************************************************** #
