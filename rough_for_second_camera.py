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

# initialising the database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(credential=cred, options={
    'databaseURL': "https://faceattendancesystem-ac890-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancesystem-ac890.appspot.com"
})

# Load the known faces and their names
known_faces = []
known_names = []
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


# Initialize some variables
mob_face_locations = []
mob_face_encodings = []
laptop_faces_name = []

# Load the video capture laptop camera
laptop_video_capture = cv2.VideoCapture(0)

# Load the mobile camera
mobile_video_capture = cv2.VideoCapture(1)
address = "http://100.73.111.114:8080/video"
mobile_video_capture.open(address)

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
    laptop_face_locations = face_recognition.face_locations(rgb_small_laptop_frame)
    laptop_face_encodings = face_recognition.face_encodings(rgb_small_laptop_frame, mob_face_locations)

    mob_face_locations = face_recognition.face_locations(rgb_small_mob_frame)
    mob_face_encodings = face_recognition.face_encodings(rgb_small_mob_frame, mob_face_locations)

    # Initialize an empty list to store the names of the detected faces
    laptop_faces_name = []

    # matching faces on laptop screen
    for face_encoding in laptop_face_encodings:
        # Check if the face matches any known faces
        matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
        name = "Unknown"

        # lower the face distance better the accuracy of the face detect
        faceDistance = face_recognition.face_distance(face_encodings=encodeListKnown,
                                                      face_to_compare=face_encoding)

        # If a match is found, use the known face name
        print("matches:", matches)
        if True in matches:
            # get the least face-distance valued Index in faceDistance List
            matchIndex = np.argmin(faceDistance)
            print("matchIndex : ", matchIndex)

            # get the employee id
            ID = employeeIDs[matchIndex]

            # import the information of employee from the database
            employeeInfo = db.reference(f'Employees/{ID}').get()
            print(employeeInfo)

            name = employeeInfo['name']
            print(name)
        # Add the name to the list of face names
        laptop_faces_name.append(name)

    # matching faces on mobile screen
    mob_faces_name = []
    for face_encoding in mob_face_encodings:
        # Check if the face matches any known faces
        matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
        name = "Unknown"

        # lower the face distance better the accuracy of the face detect
        faceDistance = face_recognition.face_distance(face_encodings=encodeListKnown,
                                                      face_to_compare=face_encoding)

        # If a match is found, use the known face name
        print("matches of mobile:", matches)
        if True in matches:
            # get the least face-distance valued Index in faceDistance List
            matchIndex = np.argmin(faceDistance)
            print("matchIndex of mobile : ", matchIndex)

            # get the employee id
            ID = employeeIDs[matchIndex]

            # import the information of employee from the database
            employeeInfo = db.reference(f'Employees/{ID}').get()
            print(employeeInfo)

            name = employeeInfo['name']
            print(f'detected mob faces name: {name}')
        # Add the name to the list of face names
        mob_faces_name.append(name)

    # Display the results
    for (mob_top, mob_right, mob_bottom, mob_left), mob_name, \
            (laptop_top, laptop_right, laptop_bottom, laptop_left), laptop_name in \
            zip(mob_face_locations, mob_faces_name, laptop_face_locations, laptop_faces_name):
        # # for top, right, bottom, left in face_locations:
        # Scale the face locations back up since the frame was resized
        mob_top *= 4
        mob_right *= 4
        mob_bottom *= 4
        mob_left *= 4

        # Draw a box around the face

        # for laptop
        cv2.rectangle(laptop_frame, (laptop_left, laptop_top), (laptop_right, laptop_bottom), (0, 0, 255), 2)
        # Draw a label with the name below the face
        cv2.rectangle(laptop_frame, (laptop_left, laptop_bottom - 35), (laptop_right, laptop_bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(laptop_frame, laptop_name, (laptop_left + 6, laptop_bottom - 6), font, 0.8, (255, 255, 255), 1)

        # for mobile
        cv2.rectangle(mob_frame, (mob_left, mob_top), (mob_right, mob_bottom), (0, 0, 255), 2)
        # Draw a label with the name below the face
        cv2.rectangle(mob_frame, (mob_left, mob_bottom - 35), (mob_right, mob_bottom), (0, 0, 255),cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX

    # Display the resulting image
    cv2.imshow('Laptop_Video_Capture', laptop_frame)
    cv2.imshow('Mobile_Video_Capture', mob_frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and destroy all windows
laptop_video_capture.release()
cv2.destroyAllWindows()

