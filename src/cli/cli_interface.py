import sys
import time
from os import system, name
import platform

empty_delim = " "
hard_divided_delim = "|"
soft_divided_delim = ":"
l_brack = "["
r_brack = "]"

ERR = "[ERR]"
INF = "[INF]"

stdout = sys.stdout
stderr = sys.stderr

def log(target, level, message, code = 0):

	message = time.ctime() + empty_delim + str(level) + l_brack + str(code) + r_brack + empty_delim + soft_divided_delim + empty_delim + message
	print(message, file = target)

def clear():
	if name == "nt":
		system("cls")
	else:
		system("clear")

def splash(version):

	def hrule():
		print("#"+38*"-"+"#")
	def box(s):
		temp = "|"
		temp += s
		temp += (40-len(s)-2)*" "
		temp += "|"
		print(temp)
	
	hrule()
	box(" superscript version: " + version)
	box(" os: " + platform.system())
	box(" python: " + platform.python_version())
	hrule()