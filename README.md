# Face Recognition Attendance System (Front-End)

> ⚠ **Note:** This repository contains only the **front-end desktop application** for a face recognition attendance system.  
> The **back-end code and SQL setup are not included**. You must create your own MySQL database with the required schema.

---

## 🚀 Prerequisites

Before running the app, make sure you have the following installed on your Windows system:

### 🔧 Software to Install

| Tool                     | Purpose                                | Download Link                                  |
|--------------------------|----------------------------------------|------------------------------------------------|
| **Python 3.10+ (64-bit)**| Core runtime                           | [python.org](https://www.python.org/downloads/windows/) |
| **MySQL Server 8+**      | Database (required)                   | [MySQL Installer](https://dev.mysql.com/downloads/installer/) |
| **Git for Windows** *(optional)* | Clone the repository         | [gitforwindows.org](https://gitforwindows.org/) |
| **Webcam**               | Required for face recognition          | Built-in or external USB webcam                |
| **CUDA GPU** *(optional)*| Boost FaceNet speed (if using TensorFlow with GPU) | [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) |

### 📦 Python Packages (installed via pip)

Make sure you install the dependencies listed in `requirements.txt`:

```txt
opencv-python
keras-facenet
tensorflow>=2.11
numpy
pandas
PySimpleGUI
pyzbar
mysql-connector-python
scikit-learn
xlrd
XlsxWriter
```

# 📂 What This Project Contains

This repo includes the modularized Python front-end that:

Uses FaceNet to recognize employee faces
Detects CODE-128 barcodes via webcam
Logs login/logout to an Excel sheet and a MySQL database
Provides an admin GUI to filter and export attendance logs
# ❌ What It Does Not Include
The MySQL database dump or schema setup
Any backend API or deployment tools
Any user interface beyond the local desktop GUI
You must manually create the MySQL database with the appropriate schema for this to work.

# ✅ What To Do Next

Once you’ve installed the required software:

## Clone this repository:
```
git clone https://github.com/your-username/Face-Recognition-Attendance-System.git
cd Face-Recognition-Attendance-System
```

## Create and activate a Python virtual environment (optional but recommended)
```
python -m venv venv
venv\Scripts\activate  # Windows
```
## Install dependencies:
```
pip install -r requirements.txt

Update your database credentials in attendance_system/db.py if needed:
connection = connect(
    host="localhost",
    user="root",
    password="your_mysql_password",
    database="Records",
)
```
## Run the app:
```
python -m attendance_system
```
#💡 Notes

The app creates folders like Daily Attendance, Source, and Attendance Data automatically on first run.
Barcode IDs must match the 5-digit employee IDs stored in the database.
Admins scan a special barcode to open the admin interface.
Face recognition uses 10 captured images per user for training.
# 🔐 Disclaimer

This code is for demonstration and academic purposes only.
It does not include production-grade security or database design.
Ensure you implement secure password handling, validation, and access control in any deployment.

