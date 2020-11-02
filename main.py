from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
# import superscript as ss

class HomeScreen(Screen):
    pass
class SettingsScreen(Screen):
    pass
class InfoScreen(Screen):
    pass

class MyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        return Builder.load_file("design.kv")



if __name__ == "__main__":
    MyApp().run()