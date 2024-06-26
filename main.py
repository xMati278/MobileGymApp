from kivy.lang import Builder
from kivymd.app import MDApp
from modules.login import LoginWindow
from modules.signup import SignupWindow
from modules.dashboard import UserTrainingPlansWindow
from managers.window_manager import WindowManager


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
