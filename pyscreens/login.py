import requests
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from http import HTTPStatus
import json
from dotenv import load_dotenv
import os

load_dotenv()
SERVER_URL = os.getenv('SERVER_URL')
TIME_TIMEOUT = int(os.getenv('TIME_TIMEOUT'))


class LoginWindow(Screen):
    username = ObjectProperty(None)
    pwd = ObjectProperty(None)

    def validate(self):
        url = SERVER_URL + 'token/'
        response = self.get_login_response(url=url)
        self.process_login_response(url=url, response=response)

    def clear_login_window(self):
        self.ids.login_error.text = ''
        self.ids.login_error.opacity = 0
        self.username.text = ''
        self.pwd.text = ''

    def get_login_response(self, url: str) -> requests.Response:
        data = {'username': self.username.text, 'password': self.pwd.text}
        response = requests.post(url, data=data, timeout=TIME_TIMEOUT)
        return response

    def process_login_response(self, response: requests.Response, url: str):
        if response.status_code == HTTPStatus.OK:
            self.manager.current = 'user_training_plans'
            response_refresh = json.loads(response.content)

            access_url = url + 'refresh/'
            access = requests.post(access_url, data=response_refresh, timeout=TIME_TIMEOUT)
            access_response = json.loads(access.content)
            access_token = access_response['access']

            self.main_app.access_token = access_token
            self.main_app.access_token_header = {'AUTHORIZATION': f'Bearer {access_token}'}

        else:
            self.clear_login_window()
            self.ids.login_error.text = 'Incorrect login details.'
            self.ids.login_error.opacity = 1
