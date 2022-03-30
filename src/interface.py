from logging import Logger as L
import datetime
import platform
import json

class Logger(L):

	file = None

	levels = {
		0: "",
		10:"[DEBUG]   ",
		20:"[INFO]    ",
		30:"[WARNING] ",
		40:"[ERROR]   ",
		50:"[CRITICAL]",
	}

	targets = []

	def __init__(self, verbose, profile, debug, file = None):
		super().__init__("tra_logger")

		self.file = file

		if file is not None:
			self.targets.append(self._send_file)

		if profile:
			self.targets.append(self._send_null)
		elif verbose:
			self.targets.append(self._send_scli)
		elif debug:
			self.targets.append(self._send_scli)
		else:
			self.targets.append(self._send_null)

	def _send_null(self, msg):
		pass

	def _send_scli(self, msg):
		print(msg)

	def _send_file(self, msg):
		f = open(self.file, 'a')
		f.write(msg + "\n")
		f.close()

	def get_time_formatted(self):
		return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S %Z")

	def log(self, level, msg):
		for t in self.targets:
			t(self.get_time_formatted() + "| " + self.levels[level] + ": " + msg)

	def debug(self, msg):
		self.log(10, msg)

	def info(self, msg):
		self.log(20, msg)

	def warning(self, msg):
		self.log(30, msg)

	def error(self, msg):
		self.log(40, msg)

	def critical(self, msg):
		self.log(50, msg)

	def splash(self, version):

		def hrule():
			self.log(0, "#"+38*"-"+"#")
		def box(s):
			temp = "|"
			temp += s
			temp += (40-len(s)-2)*" "
			temp += "|"
			self.log(0, temp)
		
		hrule()
		box(" superscript version: " + version)
		box(" os: " + platform.system())
		box(" python: " + platform.python_version())
		hrule()

	def save_module_to_file(self, module, data, results):
		f = open(module + ".log", "w")
		json.dump({"data": data, "results":results}, f, ensure_ascii=False, indent=4)
		f.close()