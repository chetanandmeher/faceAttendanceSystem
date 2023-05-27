import os
from numpy import ndarray
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# initialising the database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(credential=cred, options={
    'databaseURL': "https://faceattendancesystem-ac890-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancesystem-ac890.appspot.com"
})

# importing images
imgPathList = os.listdir('Images3')
imgList = []
# store the employee ID
employeeIDs = []
for path in imgPathList:
    imgPath = os.path.join("Images3", path)
    imgList.append(cv2.imread(imgPath))
    employeeIDs.append(path[:-4])

    # uploading the images to the storage of database\
    bucket = storage.bucket()
    blob = bucket.blob(f'Images3/{path}')
    blob.upload_from_filename(imgPath)


# print(employeeID)


# Define the encoding function which gives the encoding of faces from the images
def findEncoding(imagesList: list):
    # create a list to store encoding of images
    encodeList = []

    # opencv use color pattern BGR
    # face_recognition use color pattern RGB
    for img in imagesList:
        # changing color from BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # get the encoding of the image
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print('Encoding started.....')
encodeListKnown = findEncoding(imgList)
encodeListKnownWithIDs: list[list[ndarray] | list[any]] = [encodeListKnown, employeeIDs]
print("Encoding completed :)")

# creating a pickle file
file = open('EncodingFile.p', "wb")
pickle.dump(encodeListKnownWithIDs, file)
file.close()
print("File saved :<)")
