from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDIconButton


class TrainingPlanCard(MDCard):
    def __init__(self, name='', last_training='', **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = "50dp"
        self.padding = (10, 10, 10, 10)

        layout = GridLayout(cols=3, orientation='lr-tb', size_hint_y=1.25)
        layout.add_widget(MDLabel(text=name, theme_text_color="Primary"))
        layout.add_widget(MDLabel(text=last_training, theme_text_color="Secondary"))

        menu_items = [
            {
                "text": "Edit",
                "on_release": lambda x={'function': 'edit', 'id': self.id}: self.menu_callback(x),
            },
            {
                "text": "Delete",
                "on_release": lambda x={'function': 'delete', 'id': self.id}: self.menu_callback(x),
            },
        ]
        menu_button = MDIconButton(icon="dots-vertical")
        layout.add_widget(menu_button)

        menu = MDDropdownMenu(caller=menu_button, items=menu_items, width_mult=4)

        menu_button.bind(on_release=lambda x: menu.open())
        self.bind(on_release=lambda x: self.print_test('essa'))
        self.add_widget(layout)

    @staticmethod
    def menu_callback(text_item):
        print(text_item)

    @staticmethod
    def print_test(x):
        print(x)
