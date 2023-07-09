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
face_locations = []
face_encodings = []
face_names = []

# Load the video capture
video_capture = cv2.VideoCapture(0)


while True:
    # Read a single frame from the video capture
    ret, frame = video_capture.read()

    # flip the image latterly
    frame = cv2.flip(frame, 1)

    # Resize the frame to 1/4 size of the original to improve speed
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color to RGB color
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and their encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    print(f'face encodings:  {face_encodings}')
    # Initialize an empty list to store the names of the detected faces
    face_names = []

    for face_encoding in face_encodings:
        # Check if the face matches any known faces
        matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
        name = "Unknown"

        # lower the face distance better the accuracy of the face detect
        faceDistance = face_recognition.face_distance(face_encodings=encodeListKnown,
                                                      face_to_compare=face_encoding)

        # If a match is found, use the known face name
        print("matches:",matches)
        if True in matches:
            # get the least face-distance valued Index in faceDistance List
            matchIndex = np.argmin(faceDistance)
            print("matchIndex : ", matchIndex)

            # get the employee id
            ID = employeeIDs[matchIndex]

            # import the information of employee from the data base
            employeeInfo = db.reference(f'Employees/{ID}').get()
            print(employeeInfo)

            name = employeeInfo['name']
            print(name)
        # Add the name to the list of face names
        face_names.append(name)

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # # for top, right, bottom, left in face_locations:
        # Scale the face locations back up since the frame was resized
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # # Draw a label with the name below the face
        # cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        # font = cv2.FONT_HERSHEY_DUPLEX
        # cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and destroy all windows
video_capture.release()
cv2.destroyAllWindows()
