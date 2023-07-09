import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# initialising the database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(credential=cred,options={'databaseURL': "https://faceattendancesystem-ac890-default-rtdb.firebaseio.com/"})

# creating the employee directory in the database
ref = db.reference('Employees')

# initialising the data in json format
data = {
    "123456":
        {
            'name': 'Chetanand Meher',
            'age': 19,
            'starting year': 2023,
            'total attendance': 0,
            'department': 'Chairman',
            'last time attendance': '2023-05-26 10:28:00'



        },
    "321654":
            {
                'name': 'Ramu kaka',
                'age' : 34,
                'starting year': 2018,
                'total attendance': 0,
                'department': 'Adviser',
                'last time attendance': '2023-05-26 10:28:00'

            },
    "852741":
            {
                'name': 'Ramlaal ki biwi',
                'age' : 28,
                'starting year': 2019,
                'total attendance': 0,
                'department': 'Sweeper',
                'last time attendance': '2023-05-26 10:28:00'

            },
    "963852":
            {
                'name': 'Elonwa Mushka',
                'age' : 52,
                'starting year': 2010,
                'total attendance': 0,
                'department': 'IT',
                'last time attendance': '2023-05-26 10:28:00'
            },
    '987456':
            {
                'name': 'Makhan',
                'age' : 18,
                'starting year': 2010,
                'total attendance': 0,
                'department': 'manager',
                'last time attendance': '2023-05-26 10:28:00'
            }
}

# updating the data to the database
print('Updating data to the database....')
for key,value in data.items():
    ref.child(key).set(value)
print('Data updated. ^_+')
