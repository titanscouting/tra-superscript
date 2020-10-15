from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager , Screen
from kivy.animation import Animation
from hoverable import HoverBehavior
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
import json
from datetime import datetime
import glob
from pathlib import Path
import random

import superscript as ss

Builder.load_file('design.kv')

class HomeScreen(Screen):
    # def sign_up(self):
    #     self.manager.transition.direction = "left"
    #     self.manager.current = "sign_up_screen"
    
    # def login(self, uname, pword):
    #     with open ("users.json") as file:
    #         users = json.load(file)
    #     if uname in users and users[uname]["password"] == pword:
    #         self.manager.transition.direction = "left"
    #         self.manager.current = "login_screen_success"
    #     else:
    #         self.ids.login_wrong.text = "Incorrect Username or Password"


class RootWidget(ScreenManager):
    pass

class MainApp(App):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()