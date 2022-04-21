import os

SECRET_KEY = os.urandom(24)


def folder_url():
    upload_folder = "static/images"
    return upload_folder


SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123@localhost:5432/concert'
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOADED_FOLDER = folder_url()
