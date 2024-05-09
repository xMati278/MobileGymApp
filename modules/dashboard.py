from kivy.app import App
import requests
from kivy.uix.screenmanager import Screen
import os
from dotenv import load_dotenv
from http import HTTPStatus
import json
from icecream import ic
from kivy.logger import Logger
from datetime import datetime
from assets.training_plan_card import TrainingPlanCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.spinner import Spinner
from kivymd.uix.menu import MDDropdownMenu
load_dotenv()

SERVER_URL = os.getenv('SERVER_URL')
TIME_TIMEOUT = int(os.getenv('TIME_TIMEOUT'))


class UserTrainingPlansWindow(Screen):

    def on_enter(self, *args):
        training_plans = self.get_training_plans()
        self.create_training_plan_cards(training_plans=training_plans)

    def on_calculators_tab_press(self):
        calculator_tab = self.ids.calculator_tab
        calculator_tab.clear_widgets()
        calculator_tab.add_widget(CalculatorForm())

    @staticmethod
    def get_training_plans() -> requests.Response:
        main_app = App.get_running_app()
        if main_app.access_token:
            access_token_header = {'AUTHORIZATION': f'Bearer {main_app.access_token}'}
            training_plans = requests.get(SERVER_URL + 'readusertrainingplans/', headers=access_token_header,
                                          timeout=TIME_TIMEOUT)
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
                                        last_training=str(last_training_date),
                                        id=str(training_plan['id']))
                self.ids.training_plans_list.add_widget(card)

        else:
            Logger.error(f"Error: {training_plans.status_code}")

    @staticmethod
    def calculators_data():
        return {'wilks': 'calculator', 'dots': 'calculator'}


class CalculatorForm(MDGridLayout):
    def __init__(self, **kwargs):
        super(CalculatorForm, self).__init__(**kwargs)
        self.cols = 2
        self.spacing = '10dp'
        self.padding = '10dp'

        self.fields = []
        self.field_params = ['Body Weight (in KG)', 'Gender', 'Squat (in KG)', 'Squat reps', 'Bench Press (in KG)',
                             'Bench Press reps', 'Deadlift (in KG)', 'Deadlift reps']

        for param in self.field_params:
            if param == 'Gender':
                field = MDRaisedButton(text="Select Gender", id='gender_menu')
                field.bind(on_release=self.gender_dropdown)
            else:
                field = MDTextField(hint_text=param)

            self.add_widget(field)
            self.fields.append(field)

        self.add_widget(MDRaisedButton(text="Calculate", on_press=self.process_data))

    def gender_dropdown(self, instance):
        if 'gender_menu' in self.ids:
            self.gender_list = [
                {
                    "viewclass": "OneLineListItem",
                    "text": "Male",
                    "on_release": lambda x=f"Male": self.set_gender(x)
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Female",
                    "on_release": lambda x=f"Female": self.set_gender(x)
                }
            ]

            self.menu = MDDropdownMenu(
                caller=self.ids.gender_menu,
                items=self.gender_list,
            )

            self.menu.open()


    def process_data(self, instance):
        data_keys = ['body', 'female', 'sq', 'sq_reps', 'bp', 'bp_reps', 'dl', 'dl_reps']
        data_dict = {}
        for i, field in enumerate(self.fields):
            data_dict[data_keys[i]] = field.text

        total_info = requests.get(SERVER_URL + 'total/', params=data_dict, timeout=TIME_TIMEOUT)
        total_info_json = json.loads(total_info.content)

        self.print_data_on_screen(data=total_info_json)

    def print_data_on_screen(self, data):
        print_keys = ['bench', 'bench_dots', 'bench_ipf_gl', 'bench_wilks',
                      'deadlift', 'deadlift_dots', 'deadlift_ipf_gl', 'deadlift_wilks',
                      'squat', 'squat_dots', 'squat_ipf_gl', 'squat_wilks',
                      'total', 'total_dots', 'total_ipf_gl', 'total_wilks']

        data_to_print = []
        for key, value in data.items():
            if key in print_keys:
                if key in ['squat', 'bench', 'deadlift', 'total']:
                    data_to_print.append(key.upper())
                data_to_print.append(value)

        self.clear_widgets()
        calculator_result = CalculatorResult(data_to_print)
        self.add_widget(calculator_result)


class CalculatorResult(MDGridLayout):
    def __init__(self, data,  **kwargs):
        super(CalculatorResult, self).__init__(**kwargs)
        self.cols = 5
        self.spacing = '10dp'
        self.padding = '10dp'
        self.fields = []
        self.field_names = ['EXERCISE', 'LIFT', 'WILKS', 'DOTS', 'IPF GL']

        for item in self.field_names:
            self.add_widget(MDLabel(text=item, size_hint_y=None, height=dp(36)))

        for value in data:
            self.add_widget(MDLabel(text=str(value), size_hint_y=None, height=dp(36)))
