import requests
import os
import json
from zipfile import ZipFile
__url__ = "https://satimage-api.herokuapp.com"
# __url__="http://localhost:8000"
from pathlib import Path
import zipfile


class User():
    user_name: str
    password: str
    id: int
    token: str
    images: list
    config: dict

    def __init__(self, user_name: str, password: str):
        self.user_name = user_name
        self.password = password
        self.images = []
        self.config = {"satellite": "", "longitude": float(0), "latitude": float(
            0), "download_image_from": "NOW", "cloud_coverage": float(0)}

    def get_token_header(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }

    def login(self):
        try:
            response = requests.post(
                f"{__url__}/login", data={"username": self.user_name, "password": self.password})
            if response.status_code == 200:
                response = json.loads(response.text)
                user = response['user']
                self.config = {"satellite": user["satellite"], "longitude": user["longitude"], "latitude": user["latitude"],
                               "download_image_from": user["download_image_from"], "cloud_coverage": user["cloud_coverage"]}
                self.token = response["access_token"]
                self.id = user["id"]
                return self.token
            else:
                self.token = None
        except Exception as ex:
            print("Error in login")
            print(ex)

    def sign_up(self):
        try:
            response = requests.post(
                f"{__url__}/user", json={"email": self.user_name, "password": self.password})
            return response.text
        except Exception as ex:
            print("Sign up error")
            print(ex)

    def get_images(self):
        try:
            resp = requests.get(f"{__url__}/users/{self.id}/images",
                                headers=self.get_token_header())
            resp.text
            self.images = resp.json()
            return self.images
        except Exception as e:
            print("Couldn't get user images")
            print(e)

    def download_image(self, image_name: str, path: str):
        try:
            resp = requests.get(f"{__url__}/images/{image_name}/download",
                                headers=self.get_token_header(),
                                stream=True
                                )
            filename = resp.headers.get(
                "Content-Disposition").split("filename=")[1]
            path = os.path.join(path, image_name+".zip")
            chunk_size = 128
            with open(path, "wb") as fd:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    fd.write(chunk)
            # Create a ZipFile Object and load sample.zip in it
            with ZipFile(path, 'r') as zipObject:
                listOfFileNames = zipObject.namelist()
            for fileName in listOfFileNames:
                if fileName.endswith('.nc'):
                # Extract a single file from zip
                    zipObject.extract(fileName, '/satada/temp_py')
                    print('All the nc files are extracted')
        except Exception as e:
            print("Couldn't download image")
            print(e)

    def update_user_config(self, config: dict):
        self.config.update(config)
        try:
            requests.patch(f"{__url__}/users/{self.id}",
                           json={
                               "satellite": self.config["satellite"],
                               "longitude": self.config["longitude"],
                               "latitude": self.config["latitude"],
                               "download_image_from": self.config["download_image_from"],
                               "cloud_coverage": self.config["cloud_coverage"]
                           },
                           headers=self.get_token_header()
                           )
        except Exception as e:
            print("couldn't update user")
            print(e)


# user = User("chafik", "cgh123556")
# print(user)
# user.sign_up()
# user.login()
# user.update_user_config({"santellite": "Sentinel-4", "longitude": -5.45, "latitude": 34, "download_image_from": "20150216", "cloud_coverage": 100})
# image_name=user.get_images()[0]["name"]
# print(user.images)
# print(image_name)
# print(image_name)
# user.download_image(image_name)
