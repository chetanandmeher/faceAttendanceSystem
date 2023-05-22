# import necessary modules
import os
import pickle

import cvzone as cvzone
import numpy as np
import cv2
import face_recognition

# select the webcam
cap = cv2.VideoCapture(0)
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
print("Loadind encode file....")
file = open('EncodingFile.p', "rb")
encodeListKnownWithIDs = pickle.load(file)
encodeListKnown, employeeIDs = encodeListKnownWithIDs
print("Encode file loaded :-D")

# start the webcam
if not cap.isOpened():
    print("Error opening Web Cam.")
while True:
    # Capture frame-by-frame
    success, img = cap.read()

    # flip the image laterally
    img = cv2.flip(img, 1)

    # reducing the image size to 1/4th of original
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # get the face location in the current frame
    faceCurrFrame = face_recognition.face_locations(imgS)
    # get the encoding of the face
    encodeCurFrame = face_recognition.face_encodings(imgS,
                                                     faceCurrFrame)  # function(imageToBeEncoded, locationOfFaceInCurrentFace)

    # selecting the coordinates for the superimposing the webcam with the background and
    # different modes
    #            [height , width]
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[1]

    # comparing the known face encoding with the current face encoding
    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurrFrame):
        matches = face_recognition.compare_faces(known_face_encodings=encodeListKnown, \
                                                 face_encoding_to_check=encodeFace)
        # lower the face distance better the accuracy of the face detect
        faceDistance = face_recognition.face_distance(face_encodings=encodeListKnown, \
                                                      face_to_compare=encodeFace)
        print(f'matches: {matches}')
        print(f'faceDistance: {faceDistance}')

        # get the least face-distance valued Index in faceDistance List
        matchIndex = np.argmin(faceDistance)
        print("matchIndex : ", matchIndex)

        # check for the matches(face matching list) if the index is correct or not
        print("matches[matchIndex]: ", matches[matchIndex])
        if matches[matchIndex]:
            # print('camechooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

            ## print("Known face detected....^_^")
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
            color = (255, 0, 0)
            imgBackground = cv2.rectangle(imgBackground, start_point,
                                          end_point, color, thickness)
    # print('camechooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

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
