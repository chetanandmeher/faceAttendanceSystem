# import necessary modules
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

# creating a storage bucket
bucket = storage.bucket()

# select the webcam
cap: object = cv2.VideoCapture(0)
# set the webcam dimension
# width
cap.set(3, 640)
# height
cap.set(4, 480)

# select the background
imgBackground = cv2.imread('Resources/background.png')
# importing the different modes of the app
folderModePath = "Resources/Modes"
# get the images name list from the folder
modePathList = os.listdir(folderModePath)
# collect the images in a list
imgModeList = []
for path in modePathList:
    # get the img path by adding the folder and the image name
    imgPath = os.path.join(folderModePath, path)
    imgModeList.append(cv2.imread(imgPath))

# load the encoding file
print("Loading encode file....")
file = open('EncodingFile.p', "rb")
encodeListKnownWithIDs = pickle.load(file)
encodeListKnown, employeeIDs = encodeListKnownWithIDs
print("Encode file loaded :-D")

# selecting the mode Type
modeType = 0
# counter
counter = 0
ID = -1
imgEmployee = []

# start the webcam
if not cap.isOpened():
    print("Error opening Web Cam.")
while True:
    # Capture frame-by-frame
    success, img = cap.read()

    # flip the image laterally
    img = cv2.flip(img, 1)

    # reducing the image size to 1/4th of original
    imgS = cv2.resize(img, (0, 0), None, fx=0.25, fy=0.25)

    # convert the img color from BGR to RGB
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # get the face location in the current frame
    faceCurrFrame = face_recognition.face_locations(imgS)

    # get the encoding of the face
    # function(imageToBeEncoded, locationOfFaceInCurrentFace)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

    # selecting the coordinates for the superimposing the webcam with the background and
    # different modes
    #            [height , width]
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    if faceCurrFrame:
        # comparing the known face encoding with the current face encoding
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(known_face_encodings=encodeListKnown,
                                                     face_encoding_to_check=encodeFace)
            # lower the face distance better the accuracy of the face detect
            faceDistance = face_recognition.face_distance(face_encodings=encodeListKnown,
                                                          face_to_compare=encodeFace)
            print(f'matches: {matches}')
            print(f'faceDistance: {faceDistance}')

            # get the least face-distance valued Index in faceDistance List
            matchIndex = np.argmin(faceDistance)
            print("matchIndex : ", matchIndex)

            # check for the matches(face matching list) if the index is correct or not
            print("matches[matchIndex]: ", matches[matchIndex])
            if matches[matchIndex]:
                print(
                    'camechooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
                print("Known face detected....^_^")
                # making a rectangle around the face
                y1, x2, y2, x1 = faceLoc
                # multiplying the co-ords by 4 because we reduce the image size by 4 initially
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                # giving offset to the bounding box
                bbox = (55 + x1), (162 + y1), (x2 - x1), (y2 - y1)
                # imgBackground = cvzone.cornerRect(img=imgBackground,bbox=bbox,rt=10)
                start_point = ((55 + x1), (162 + y1))
                end_point = ((55 + x1) + (x2 - x1), (162 + y1) + (y2 - y1))
                thickness = 2
                color = (0, 255, 0)
                imgBackground = cv2.rectangle(imgBackground, start_point,
                                              end_point, color, thickness)
                ID = employeeIDs[matchIndex]
                print(f'ID: {ID}')
                print(
                    'camechoooooooooooooooooooooooooooooooooooooooooooooooooo0ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
                print(counter)

                if counter == 0:
                    # cvzone.putTextRect(imgBackground, "Loading....", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    print(counter)
                    modeType = 1
        # checking for the counter to download the information fom the database
        if counter != 0:
            if counter == 1:
                # import the information of employee from the data base
                employeeInfo = db.reference(f'Employees/{ID}').get()
                print(employeeInfo)

                # get the image from the database
                blob = bucket.get_blob(f'Images3/{ID}.png')

                # comment needed ##########################################################################################
                array = np.frombuffer(buffer=blob.download_as_string(), dtype=np.uint8)
                imgEmployee = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # update the attendance
                ref = db.reference(f'Employees/{ID}')
                datetimeObject = datetime.strptime(employeeInfo['last time attendance'], '%Y-%m-%d %H:%M:%S')
                secondElapsed = (datetime.now() - datetimeObject).total_seconds()
                print("secondElapsed: ", secondElapsed)

                if secondElapsed > 30:
                    # increase the attendance bu 1
                    employeeInfo['total attendance'] += 1
                    ref.child('total attendance').set(employeeInfo['total attendance'])
                    # updating the last time attendance
                    currTime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
                    ref.child('last time attendance').set(currTime)
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType!=3:
                # selecting the mod type corresponding to the counter
                if 10 < counter < 20:
                    modeType = 2
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    # putting the name on the background image
                    (w, h), _ = cv2.getTextSize(text=employeeInfo['name'],fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, thickness=1)
                    offset = (414 - w)//2
                    cv2.putText(img=imgBackground, text=employeeInfo["name"],org=(808+offset, 450), fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=1, color=(0, 0, 0), thickness=1)
                    # age
                    cv2.putText(img=imgBackground, text=str(ID), org=(1006, 493), fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=0.6, color=(255, 255, 255), thickness=1)
                    # department
                    cv2.putText(img=imgBackground, text=str(employeeInfo["department"]), org=(1006, 550),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.6, color=(255, 255, 255), thickness=1)
                    # starting year
                    cv2.putText(img=imgBackground, text=str(employeeInfo["starting year"]), org=(1125, 625),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.6, color=(100, 100, 100), thickness=1)
                    # total attendance
                    cv2.putText(img=imgBackground, text=str(employeeInfo["total attendance"]), org=(865, 125),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(255, 255, 255), thickness=1)

                    imgBackground[175:175+216, 909:909+216] = imgEmployee

                counter += 1
                print("Counter: ", counter)
                if counter > 20:
                    counter = 0
                    modeType = 0
                    employeeInfo = []
                    imgEmployee = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    # show the webcam img
    ## cv2.imshow('Webcam', flippedImg)
    # show the background
    cv2.imshow("Face Attendance", imgBackground)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # if frame is read correctly, ret is True
    if not success:
        print("Can't retrieve frame - stream may have ended. Exiting..")
        break
# Closing the window
print("Video has ended.")
cv2.waitKey(1)
cv2.destroyAllWindows()
