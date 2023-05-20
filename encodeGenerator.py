import os

from numpy import ndarray
from typing import List, Any

import cv2
import face_recognition
import pickle


# importing images
imgPathList = sorted(os.listdir('images'))      # the order : ['1.png', '10.png', '11.png', '12.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png', '9.png']
imgList = []
# store the employee ID
employeeIDs = []
for path in imgPathList:
    imgPath = os.path.join("images",path)
    imgList.append(cv2.imread(imgPath))

    employeeIDs.append(path[:-4])
# print(employeeID)

# Define the encoding function which gives the encoding of faces from the images
def findEncoding(imagesList: List):
    # create a list to store encoding of images
    encodeList = []

    # opencv use color pattern BGR
    # face_recognintion use color pattern RGB
    for img in imagesList:
        # changing color from BGR to RGB
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # get the encoding of the image
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print('Encoding started.....')
encodeListKnown = findEncoding(imgList)
encodeListKnownWithIDs: list[list[ndarray] | list[Any]] = [encodeListKnown,employeeIDs]
print("Encoding completed :)")

# creating a pickle file
file = open('EncodingFile.p',"wb")
pickle.dump(encodeListKnownWithIDs,file)
file.close()
print("File saved :<)")

