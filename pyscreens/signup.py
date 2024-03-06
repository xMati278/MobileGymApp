import requests
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from http import HTTPStatus
import json
from dotenv import load_dotenv
import os
from typing import Dict
from email_validator import EmailNotValidError, validate_email

load_dotenv()
SERVER_URL = os.getenv('SERVER_URL')
TIME_TIMEOUT = int(os.getenv('TIME_TIMEOUT'))


class SignupWindow(Screen):
    username = ObjectProperty(None)
    pwd = ObjectProperty(None)
    email = ObjectProperty(None)

    def validate(self):
        data = self.validate_signup_data()
        print(data)
        self.create_account(data=data)

    def clear_signup_window(self):
        self.ids.signup_error.text = ''
        self.ids.signup_error.opacity = 0
        self.username.text = ''
        self.pwd.text = ''
        self.email.text = ''

    def validate_signup_data(self) -> Dict[str, str]:
        if self.pwd.text == '' or len(self.pwd.text) <= 8:
            self.clear_signup_window()
            self.ids.signup_error.text = 'Your password is too short.'
            self.ids.signup_error.opacity = 1
        else:
            if not(self.is_valid_email(self.email.text)):
                self.clear_signup_window()
                self.ids.signup_error.text = 'Your email is not correct.'
                self.ids.signup_error.opacity = 1
            else:
                data = {'username': self.username.text, 'password': self.pwd.text, 'email': self.email.text}
                return data

    def create_account(self, data):
        url = SERVER_URL + 'register/'
        response = requests.post(url, data=data, timeout=TIME_TIMEOUT)
        response_data = json.loads(response.content)

        if response.status_code == HTTPStatus.BAD_REQUEST:
            self.clear_signup_window()
            self.ids.signup_error.text = response_data['error']
            self.ids.signup_error.opacity = 1

        if response.status_code == HTTPStatus.CREATED:
            self.manager.transition.direction = "up"
            self.manager.current = 'login'
            self.clear_signup_window()

    @staticmethod
    def is_valid_email(email):
        try:
            validate_email(email, check_deliverability=True)
            return True

        except EmailNotValidError:
            return False
