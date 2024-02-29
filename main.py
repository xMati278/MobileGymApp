import json
from datetime import datetime
from http import HTTPStatus
from typing import Dict

import requests
from email_validator import EmailNotValidError, validate_email
from icecream import ic
from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu

SERVER_URL = 'http://127.0.0.1:8000/api/'


class TrainingPlanCard(MDCard):
    def __init__(self, name='', last_training='', **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = "50dp"
        self.padding = (10, 10, 10, 10)

        layout = GridLayout(cols=3, pos_hint={'center_y': 0.5}, size_hint_y=None)
        layout.add_widget(MDLabel(text=name, theme_text_color="Primary"))
        layout.add_widget(MDLabel(text=last_training, theme_text_color="Secondary", halign="center"))

        menu_items = [
            {
                "text": "Edit",
                "on_release": lambda x="Edit": self.menu_callback(x),
            },
            {
                "text": "Delete",
                "on_release": lambda x="Delete": self.menu_callback(x),
            },
        ]
        menu_button = MDIconButton(icon="dots-vertical")
        layout.add_widget(menu_button)

        menu = MDDropdownMenu(caller=menu_button, items=menu_items, width_mult=4)

        menu_button.bind(on_release=lambda x: menu.open())

        self.add_widget(layout)

    def menu_callback(self, text_item):
        print(text_item)


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
        response = requests.post(url, data=data)
        return response

    def process_login_response(self, response: requests.Response, url: str):
        if response.status_code == HTTPStatus.OK:
            self.manager.current = 'user_training_plans'
            response_refresh = json.loads(response.content)

            access_url = url + 'refresh/'
            access = requests.post(access_url, data=response_refresh)
            access_response = json.loads(access.content)
            access_token = access_response['access']

            self.main_app.access_token = access_token
            self.main_app.access_token_header = {'AUTHORIZATION': f'Bearer {access_token}'}

        else:
            self.clear_login_window()
            self.ids.login_error.text = 'Incorrect login details.'
            self.ids.login_error.opacity = 1


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
        response = requests.post(url, data=data)
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


class WindowManager(ScreenManager):
    pass


class UserTrainingPlansWindow(Screen):

    def on_enter(self, *args):
        training_plans = self.get_training_plans()
        self.create_training_plan_cards(training_plans=training_plans)

    @staticmethod
    def get_training_plans() -> requests.Response:
        main_app = App.get_running_app()
        if main_app.access_token:
            access_token_header = {'AUTHORIZATION': f'Bearer {main_app.access_token}'}
            training_plans = requests.get(SERVER_URL + 'readusertrainingplans/', headers=access_token_header)
            return training_plans
        else:
            Logger.warning("Access token is not set.")

    def create_training_plan_cards(self, training_plans: requests.Response):
        if training_plans.status_code == HTTPStatus.OK:
            training_plans_response = json.loads(training_plans.content)
            self.ids.training_plans_list.clear_widgets()
            for training_plan in training_plans_response:
                ic(training_plan)
                if training_plan['last_training'] is not None:
                    last_training_date = f"Last Training:" \
                                         f" {datetime.strptime(training_plan['last_training'], '%Y-%m-%dT%H:%M:%SZ')}"
                else:
                    last_training_date = '-'
                card = TrainingPlanCard(name=training_plan['name'],
                                        last_training=str(last_training_date))
                self.ids.training_plans_list.add_widget(card)

        else:
            Logger.error(f"Error: {training_plans.status_code}")


class MainApp(MDApp):
    refresh_token = None
    access_token = None
    access_token_header = None

    def build(self):
        Builder.load_file('main.kv')
        sm = WindowManager()

        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Red'
        self.theme_cls.primary_hue = '700'

        login_window = LoginWindow(name='login')
        login_window.main_app = self
        sm.add_widget(login_window)
        sm.add_widget(SignupWindow(name='signup'))
        sm.add_widget(UserTrainingPlansWindow(name='user_training_plans'))

        return sm
