import os
import cv2
from keras_facenet import FaceNet
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from pyzbar.pyzbar import decode
from datetime import datetime
import csv
import sys
import contextlib
import mysql.connector
import PySimpleGUI as sg
import mysql.connector
from mysql.connector import Error
import pandas as pd




#backend
try:
    # Establish a connection
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Pranav2530',
        database='Records'
    )
    if connection:
        print('Connected to database')
    # Do database operations here

except Error:
    print(f"Error connecting to Database: {Error}")


# Global declarations

emp_embeddings= r".\Source"
emp_attendance=r'.\Daily Attendance'
emp_data= r".\Attendace Data"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
img_shape= None
embedder = FaceNet()
os.makedirs(emp_attendance, exist_ok=True)
os.makedirs(emp_data, exist_ok=True)

# Generating the current time and date
current_datetime= datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# File creation
filename= f'Attendance_{current_datetime[:10]}.xlsx'

# Check if the file already exists
if not os.path.exists(os.path.join(emp_attendance, filename)):

    # Create an empty DataFrame
    df = pd.DataFrame(columns=['Employee ID','Name','Batch ID','Log in time','Log out time','Mail','Defaulter'])

    # Create an Excel writer using pandas
    writer = pd.ExcelWriter(os.path.join(emp_attendance, filename), engine='xlsxwriter')

    # Write the DataFrame to the Excel file
    df.to_excel(writer, index=False)


    # Save the Excel file
    writer._save()

attendance_path= os.path.join(emp_attendance, filename)

def attendance(emp_id):
    emp_id= int(emp_id)
    current_time = datetime.now().strftime("%H:%M")
    logs = pd.read_excel(attendance_path)  # Replace 'filename.xlsx' with the actual filename and path
    emp_details= pd.read_csv(os.path.join(emp_embeddings, str(emp_id), 'info.csv'))
    # Check if employee ID exists in the logs
    if emp_id in logs['Employee ID'].values:
        # Update log out time for matching employee ID
        if logs.loc[logs['Employee ID'] == emp_id, 'Log out time'].any():
            print('Already logged out')
            print('---------------')
            scan()
        else:
            try:
                if connection.is_connected():
                    # Create a cursor object to execute queries
                    cursor = connection.cursor()
                    cursor.execute('USE Records')
                    date = datetime.now().strftime("%Y-%m-%d")
                    time = datetime.now().strftime("%H:%M:%S")

                    query = f"UPDATE attendance SET log_out_time = '{time}' WHERE attendance_date = '{date}' AND emp_id= '{emp_id}'"  # Execute the query
                    cursor.execute(query)

                    # Commit the changes to the database
                    connection.commit()

                    # Close the cursor and connection
                    cursor.close()


            except Exception as e:
                print("An error occurred:", str(e))

            logs.loc[logs['Employee ID'] == emp_id, 'Log out time']= current_time
            if current_time < '18;00':
                if logs.loc[logs['Employee ID']== emp_id, 'Defaulter'].any():
                    logs.loc[logs['Employee ID'] == emp_id, 'Defaulter']= 'Came Late, Left early'
                else:
                    logs.loc[logs['Employee ID'] == emp_id, 'Defaulter'] = 'Left early'
            logs.to_excel(attendance_path, index=False)  # Save the updated DataFrame back to the Excel file
            print(f"Employee {emp_id} logged out at {current_time}")
            print('---------------')
            scan()
    else:
        try:
            if connection.is_connected():
                # Create a cursor object to execute queries
                cursor = connection.cursor()
                cursor.execute('USE Records')
                date= datetime.now().strftime("%Y-%m-%d")
                time= datetime.now().strftime("%H:%M:%S")

                query = f"INSERT INTO attendance (attendance_date, log_in_time, emp_id) VALUES ('{date}', '{time}', '{emp_id}')"


                # Execute the query
                cursor.execute(query)

                # Commit the changes to the database
                connection.commit()

                # Close the cursor and connection
                cursor.close()


        except Exception as e:
            print("An error occurred:", str(e))
        if current_time <= '09:05':
        # Employee ID does not exist in the logs, add new entry
            entry = {
            'Employee ID': int(emp_id),
            'Name': emp_details.columns[0],
            'Batch ID': emp_details.columns[1],
            'Log in time': current_time,
            'Mail': emp_details.columns[2]
        }
        else:
            entry= {
                'Employee ID': int(emp_id),
                'Name': emp_details.columns[0],
                'Batch ID': emp_details.columns[1],
                'Log in time': current_time,
                'Mail': emp_details.columns[2],
                'Defaulter': 'Came Late'
            }

        logs = logs._append(entry, ignore_index=True)
        logs.to_excel(attendance_path, index=False)  # Save the updated DataFrame back to the Excel file
        print(f"Employee {emp_id} added to the attendance logs, log in time {current_time}")
        print('---------------')
        scan()


def get_attendance(result):
    import datetime

    # Create a DataFrame with the result
    df_attendance = pd.DataFrame(columns=['emp_id', 'emp_name', 'batch_id', 'attendance_date', 'log_in_time', 'log_out_time', 'mail'])

    print('starting download')
    for row in result:
        # Assuming the current date is available as `current_date`
        current_date = datetime.datetime.now().date()

        log_in_datetime = datetime.datetime.combine(current_date, datetime.time()) + row[5]
        log_out_datetime = datetime.datetime.combine(current_date, datetime.time()) + row[6]

        # Format the datetimes as strings
        log_in_time = log_in_datetime.strftime("%H:%M")
        log_out_time = log_out_datetime.strftime("%H:%M")



        # Create a list for the new row
        row = [row[0], row[1], row[2], row[4].strftime("%Y-%m-%d"), log_in_time, log_out_time, row[3]]

        # Append the new row to the DataFrame
        df_attendance.loc[len(df_attendance)] = row

    def file_creation(name, n=0):
        if n == 0:
            if os.path.exists(os.path.join(emp_data, name)):
                file = os.path.join(emp_data, f'attendance_data_{datetime.datetime.now().date()}({n + 1}).xlsx')
                if os.path.exists(file):
                    return file_creation(file, n + 1)
                else:
                    return file
            else:
                return os.path.join(emp_data, name)
        else:
            file = os.path.join(emp_data, f'attendance_data_{datetime.datetime.now().date()}({n}).xlsx')
            if os.path.exists(file):
                return file_creation(name, n + 1)  # Use `name` instead of `filename`
            else:
                return filename


    filename = f'attendance_data_{datetime.datetime.now().date()}.xlsx'

    file_path= file_creation(filename)
    try:
        # Save DataFrame as Excel file
        df_attendance.to_excel(file_path, index=False)
        print(f'Attendance data saved as {filename}')
    except Exception as e:
        print(f"Error saving the attendance data: {e}")



def admin_page():
    def query(start_date=None, end_date=None, batch_id=None, emp_name=None):
        cursor = connection.cursor()
        cursor.execute('USE RECORDS')
        query = "SELECT * FROM emp JOIN attendance ON emp.emp_id = attendance.emp_id"

        conditions = []

        if start_date:
            conditions.append(f"attendance_date >= '{start_date}'")

        if end_date:
            conditions.append(f"attendance_date <= '{end_date}'")

        if batch_id:
            conditions.append(f"batch_id = {batch_id}")

        if emp_name:
            conditions.append(f"emp_name = '{emp_name}'")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def get_distinct_ids(attribute):
        cursor = connection.cursor()
        query1 = "USE RECORDS"
        query2 = f"SELECT DISTINCT {attribute} FROM emp"
        cursor.execute(query1)
        cursor.execute(query2)
        result = cursor.fetchall()
        distinct_ids = []
        for i in result:
            distinct_ids.append(i[0])
        distinct_ids.append('All')
        return distinct_ids

    names = get_distinct_ids('emp_name')
    batch_ids = get_distinct_ids('batch_id')

    start_date = None
    end_date = None
    batch_id = None
    emp_name = None

    layout = [
        [sg.Text('Start Date:'), sg.Input(key='-STARTDATE-', enable_events=True, size=(20, 1)),
         sg.CalendarButton('Select', target='-STARTDATE-', key='-STARTDATE_BUTTON-', format='%Y-%m-%d')],
        [sg.Text('End Date:'), sg.Input(key='-ENDDATE-', enable_events=True, size=(20, 1)),
         sg.CalendarButton('Select', target='-ENDDATE-', key='-ENDDATE_BUTTON-', format='%Y-%m-%d')],
        [sg.Text('Batch ID:'), sg.Combo(batch_ids, key='-BATCHID-', enable_events=True, size=(20, 1))],
        [sg.Text('Employee Name:'), sg.Combo(names, key='-EMPNAME-', enable_events=True, size=(20, 1))],
        [sg.Button('Filter'), sg.Button('Download'), sg.Button('Exit')],
        [sg.Output(size=(140, 30))]
    ]
    window = sg.Window('Attendance Filter', layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        if event == '-STARTDATE_BUTTON-':
            window['-STARTDATE-'].update(values['-STARTDATE-'])
        if event == '-ENDDATE_BUTTON-':
            window['-ENDDATE-'].update(values['-ENDDATE-'])
        if event == 'Filter':
            start_date = values['-STARTDATE-']
            end_date = values['-ENDDATE-']
            if values['-BATCHID-']:
                if values['-BATCHID-'] == 'All':
                    batch_id = None
                else:
                    batch_id = values['-BATCHID-']
            if values['-EMPNAME-']:
                if values['-EMPNAME-'] == 'All':
                    emp_name= None
                else:
                    emp_name = values['-EMPNAME-']
            result = query(start_date=start_date, end_date=end_date, batch_id=batch_id, emp_name=emp_name)

            # Display the result
            for row in result:
                print(f'emp_id: {row[0]}     Name: {row[1]}     Batch_id: {row[2]}      Date: {row[4]}      Login_time: {row[5]}        Logout_time: {row[6]}       Email: {row[3]}')
        if event == 'Download':
            start_date = values['-STARTDATE-']
            end_date = values['-ENDDATE-']
            if values['-BATCHID-'] != 'All':
                batch_id = values['-BATCHID-']
            if values['-EMPNAME-'] != 'All':
                emp_name = values['-EMPNAME-']


            result = query(start_date=start_date, end_date=end_date, batch_id=batch_id, emp_name=emp_name)

            get_attendance(result)
            print('Attendance Downloaded, Can be found in Attendace Data')


    window.close()


def get_image_paths(emp_id):
    captured_images_dir = os.path.join(emp_embeddings, str(emp_id))
    image_paths = []
    for file_name in os.listdir(captured_images_dir):
        if file_name.startswith(str(emp_id)) and file_name.endswith(".jpg"):
            image_paths.append(os.path.join(captured_images_dir, file_name))
    return image_paths


def get_embeddings(emp_id):
    image_paths = get_image_paths(emp_id)
    embeddings = []
    for image_path in image_paths:
        if image_path.endswith(".jpg"):
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            img = cv2.resize(img, (160, 160))  # Resize to (160, 160) as expected by FaceNet model
            img = img.astype('float32')  # Convert to float32
            img = np.expand_dims(img, axis=0)  # Add batch dimension

            # Temporarily suppress the output of a specific part of the script
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    # Perform the embedding process using FaceNet
                    embedding = embedder.embeddings(img)


            embeddings.append(embedding[0])

    return embeddings


def save_embeddings(emp_id, embeddings, status= 0):
    output_dir = os.path.join(emp_embeddings, str(emp_id))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    embeddings_path = os.path.join(output_dir, f'{emp_id}_embeddings.pkl')
    with open(embeddings_path, 'wb') as file:
        pickle.dump(embeddings, file)

    # Delete the captured images
    image_files = [file for file in os.listdir(output_dir) if file.endswith('.jpg')]
    for image_file in image_files:
        image_path = os.path.join(output_dir, image_file)
        os.remove(image_path)


def load_embeddings(emp_id):
    output_dir = os.path.join(emp_embeddings, str(emp_id))
    embeddings_path = os.path.join(output_dir, f'{emp_id}_embeddings.pkl')
    with open(embeddings_path, 'rb') as file:
        embeddings = pickle.load(file)
    return embeddings


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
img_shape= None


def image_preprocessing(path):
    """Conducts the entire preprocessing using the functions crop_face() and convert_to_grayscale"""

    image_dir = path  # Replace with your image directory path
    count = 1

    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg"):
            # Process the image
            image_path = os.path.join(image_dir, filename)
            image = cv2.imread(image_path)

            # Detect faces in the image
            faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Crop and replace faces
            for (x, y, w, h) in faces:
                global face_
                face_ = image[y:y + h, x:x + w]
                face_ = cv2.resize(face_, (160, 160))  # Desired dimensions

            Face= face_

            # Replace the original image with the cropped face
            cv2.imwrite(image_path, Face)
            count += 1


def locate_face(image):
    """In order to operate on a face we must locate a face first
    this function will locate the face and return it"""
    # using the CascadeClassifier to classify faces. Pre_trained face classifier model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert color
    face = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(100, 100))

    return face


def capture(emp_id, status=1):
    """Once the face has been detected and needs to be learnt, we need to capture multiple pictures of the person and
    then learn using those pictures. It takes 2 parameters, Emp_ID and 'n' number of pictures.
    Emp_id will help us locate these pictures later.
    n is the number of pictures we want of the user"""

    # Open the webcam
    video_capture = cv2.VideoCapture(0)

    # Directory to store the captured images
    output_dir = os.path.join(emp_embeddings, str(emp_id))

    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Counter for captured images
    num = 0

    if status == 1:

        layout = [
            [sg.Text('Enter your name:')],
            [sg.Input(key='-NAME-')],
            [sg.Text('Enter your Batch ID:')],
            [sg.Input(key='-Batch ID-')],
            [sg.Text('Enter your email:')],
            [sg.Input(key='-EMAIL-')],
            [sg.Checkbox('Admin', key='-ADMIN-')],  # Add the checkbox for admin
            [sg.Text('Enter Admin Password:')],
            [sg.Input(key='-PASSWORD-')],
            [sg.Button('Submit')]
        ]
        window = sg.Window('Employee details', layout, location=(560, 180))

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == 'Submit':
                break

        if event == 'Submit':
            global Name, BatchID, Mail, is_admin
            Name = values['-NAME-']
            BatchID = values['-Batch ID-']
            Mail = values['-EMAIL-']
            is_admin = values['-ADMIN-']
            pw= values['-PASSWORD-']
            if is_admin == True:
                if pw !='nsbt': #password 
                    window.close()
                    print('Incorrect password')
                    return capture(emp_id, 1)
                else:
                    print('Admin password verified')
            window.close()


        file_path = os.path.join(emp_embeddings, str(emp_id), "info.csv")
        # Open the file in append mode to add new data
        with open(file_path, 'a', newline='') as details:
            writer = csv.writer(details)
            writer.writerow([Name, BatchID, Mail])
        try:
            if connection.is_connected():
                # Create a cursor object to execute queries
                cursor = connection.cursor()
                cursor.execute('USE Records')
                if is_admin == False:
                    query = f"INSERT INTO emp (emp_id, emp_name, batch_id, email) VALUES ('{emp_id}','{Name}','{BatchID}','{Mail}')"
                else:
                    query = f"INSERT INTO admin (emp_id, emp_name, email) VALUES ('{emp_id}','{Name}','{Mail}')"

                # Execute the query
                cursor.execute(query)

                # Commit the changes to the database
                connection.commit()

                # Close the cursor and connection
                cursor.close()

        except Exception as e:
            print("An error occurred:", str(e))


    window = None

    while True:
        if status == 0:


            # Automatically capture and save a single image
            ret, frame = video_capture.read()
            flipped_frame = cv2.flip(frame, 1)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Convert the image to grayscale
            gray = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2GRAY)

            # Perform face detection
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Check if any faces are detected
            if len(faces) > 0:
                image_path = os.path.join(output_dir, f'{emp_id}_captured_image_temp.jpg')
                cv2.imwrite(image_path, flipped_frame)
                print('Temporary image saved')
                # Release the video capture object and close the window
                video_capture.release()
                cv2.destroyAllWindows()
                return True
            else:
                print("No face Detected, Scan Again")
                # Release the video capture object and close the window
                video_capture.release()
                cv2.destroyAllWindows()
                return False


        if window is None:
            layout = [
                [sg.Text('Click the Capture button to capture images')],
                [sg.Image(key='-IMAGE-')],
                [sg.Button('Capture')]
            ]
            window = sg.Window('Image Capture', layout, location=(720,160))

        event, values = window.read(timeout=20)

        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break

        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Flip the frame horizontally
        flipped_frame = cv2.flip(frame, 1)

        # Detect faces in the frame
        faces = locate_face(frame)

        # Ensure only one face is detected
        if len(faces) == 1:
            # Resize the frame to fit the window
            frame_resized = cv2.resize(flipped_frame, (640, 480))
            # Convert the frame to a format suitable for PySimpleGUI
            img_bytes = cv2.imencode('.png', frame_resized)[1].tobytes()

            # Update the image element in the GUI
            window['-IMAGE-'].update(data=img_bytes)

            if event == 'Capture':
                num += 1
                image_path = os.path.join(output_dir, f'{emp_id}_captured_image_{num}.jpg')
                cv2.imwrite(image_path, frame)
                print(f'Image {num} saved.')

                if num == 10:
                    window.close()
                    break



    # Release the video capture object and close the window
    video_capture.release()
    cv2.destroyAllWindows()


def detect_face(emp_id, new_user):
    """To learn a face we must detect a face. Detect face take 2 parameters. new_user: takes value 0 or 1. 0 means it
    is an existing user and therefore the face needs to be recognized,  else it is a new user and the face needs to be
    learnt.  Emp_Id: will give is the key-value pair of Emp_Id-learnt face from our database that we have to compare the
    current face to."""
    # Open the webcam
    video_capture = cv2.VideoCapture(0)
    face_detected = False
    while not face_detected:
        # Capture frame-by-frame
        ret, image = video_capture.read()

        # Detect faces in the frame
        face = locate_face(image)
        if len(face) != 0:
            face_detected = True
    # if it is not a new user we recognize which user is it
    if new_user == 0:
        return recognize_face(emp_id)
    # if it is a new user we learn their face
    return learn_face(emp_id)

def learn_face(emp_id):
    # Capture Images
    capture(emp_id,1)
    path_for_emp_images = os.path.join(emp_embeddings, str(emp_id))
    # Preprocess the captured images
    print('Start Processing')
    image_preprocessing(path_for_emp_images)
    print('Processing Done')
    # Extract facial features using a face recognition model
    embeddings = get_embeddings(emp_id)
    # Save the embeddings to a file
    save_embeddings(emp_id, embeddings)

    print(f'Face of employee {emp_id} learnt.')
    print('---------------')
    scan()

def recognize_face(emp_id, threshold=0.6):

    is_there_a_face= capture(emp_id, 0)
    if is_there_a_face == True:

        path_for_emp_images = os.path.join(emp_embeddings, str(emp_id))

        # Preprocess the captured image
        image_preprocessing(path_for_emp_images)


        # Get the embeddings of the captured face
        captured_embeddings = get_embeddings(emp_id)

        # Load the stored embeddings of known faces
        stored_embeddings = load_embeddings(emp_id)  # Implement this function to load the stored embeddings

        # Compare the captured embeddings with the stored embeddings
        similarities = []
        for captured_embedding in captured_embeddings:
            for stored_embedding in stored_embeddings:
                similarity = cosine_similarity([captured_embedding], [stored_embedding])[0][0]
                similarities.append(similarity)

        # Find the highest similarity
        highest_similarity = max(similarities)

        # Determine if the captured face matches any known face
        if highest_similarity >= threshold:
            #event_text, values_ = text_window.read(timeout=1)
            print("Face recognized!")
            print("Matching employee ID: ", emp_id)
            if admin == False:
                attendance(emp_id)
            else:
                text_window.close()
                admin_page()
                frontend()

        else:
            print("Face not recognized!")
            print('---------------')
            scan()
    else:
        scan()



def decode_barcode(frame):
    #event_text, values_ = text_window.read(timeout=1)
    """This Function decodes a barcode"""
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Decode barcodes in the frame
    barcodes = decode(gray)

    # Process each detected barcode
    for barcode in barcodes:
        # Extract the barcode data
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        try:
            if connection.is_connected():
                # Create a cursor object to execute queries

                cursor = connection.cursor()
                cursor.execute('USE Records')

                # Execute the query
                query = f"SELECT EXISTS(SELECT 1 FROM admin WHERE emp_id = {barcode_data})"
                cursor.execute(query)

                # Fetch the result
                result = cursor.fetchone()

                if result[0] == 1:
                    global admin
                    admin = True

                # Close the cursor
                cursor.close()

        except Error as e:
            print("An error occurred:", str(e))

        if barcode_type == 'CODE128' and len(barcode_data)== 5:
            return barcode_data
        else:
            print('Hold still, scan again.')
            scan()
def scan():
    global admin
    admin= False


    layout = [
        [sg.Image(filename='', key='-IMAGE-')]
    ]
    cap = cv2.VideoCapture(0)


    # Create the window


    window = sg.Window('Barcode Scan', layout, location=(620,160))


    while True:
        event, values = window.read(timeout=20)
        event_text, values_ = text_window.read(timeout=1)

        if event == sg.WINDOW_CLOSED:
            return None
        if event_text == sg.WINDOW_CLOSED:
            return None

        # Read a frame from the webcam
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        # Resize the frame to fit the window
        frame_resized = cv2.resize(frame, (640, 480))

        # Convert the frame to a format suitable for PySimpleGUI
        img_bytes = cv2.imencode('.png', frame_resized)[1].tobytes()

        # Update the image element in the GUI
        window['-IMAGE-'].update(data=img_bytes)

        # Decode barcodes in the frame
        global emp_id
        emp_id = decode_barcode(frame)



        # If a barcode is detected, break the loop
        if emp_id is not None:
            print(emp_id)
            break


    # Release the video capture object and close any open windows
    cap.release()

    # Print the decoded barcode outside the loop
    if emp_id is not None:

        path= os.path.join(emp_embeddings, emp_id)
        if not os.path.exists(path):
            window.close()
            learn_face(emp_id)
        else:
            window.close()
            recognize_face(emp_id)

def frontend():

    sg.theme('Light Blue4')
    text_layout = [
        [sg.Output(size=(40, 25), key='-OUTPUT-')]
    ]

    global text_window
    text_window = sg.Window("", text_layout, location=(260, 180))


    # define the window layout
    layout = [[sg.Text('Attendance System', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image')],
              [sg.Button('Start', size= (10, 1), font='Helvetica 14')]]

    # create the window and show it without the plot
    window = sg.Window('Face Recognition System',
                       layout, finalize= True)

    while True:
        event, values = window.read(timeout=20)
        if event == 'Start':
            window.close()
            return scan()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break

frontend()
# Redirect both stdout and stderr to a null device
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')