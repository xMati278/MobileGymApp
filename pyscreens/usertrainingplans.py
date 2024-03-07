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
from assets.trainingplancard import TrainingPlanCard

load_dotenv()
SERVER_URL = os.getenv('SERVER_URL')
TIME_TIMEOUT = int(os.getenv('TIME_TIMEOUT'))


class UserTrainingPlansWindow(Screen):

    def on_enter(self, *args):
        training_plans = self.get_training_plans()
        self.create_training_plan_cards(training_plans=training_plans)

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
