from kivy.lang import Builder

from kivymd.uix.screen import Screen
from kivymd.uix.list import OneLineListItem, MDList, TwoLineListItem, ThreeLineListItem
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.uix.scrollview import ScrollView


from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivymd.uix.menu import MDDropdownMenu, MDMenuItem

from kivymd.app import MDApp
# import superscript as ss

# from tra_analysis import analysis as an
import data as d
from collections import defaultdict
import json
import math
import numpy as np
import os
from os import system, name
from pathlib import Path
from multiprocessing import Pool
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import time
import warnings

# global exec_threads


# Screens
class HomeScreen(Screen):
	pass
class SettingsScreen(Screen):
	pass
class InfoScreen(Screen):
	pass

class StatsScreen(Screen):
	pass


class MyApp(MDApp):
	def build(self):
		self.theme_cls.primary_palette = "Red"
		return Builder.load_file("design.kv")
	def test():
		print("test")


if __name__ == "__main__":
	MyApp().run()