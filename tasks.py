import json
import superscript as su
import threading

__author__ = (
	"Arthur Lu <learthurgo@gmail.com>",
)

class Tasker():

	match_ = False
	metric_ = False
	pit_ = False

	match_enable = True
	metric_enable = True
	pit_enable = True

	config = {}

	def __init__(self):

		self.config = su.load_config("config.json")

	def match(self):

		self.match_ = True

		apikey = self.config["key"]["database"]
		competition = self.config["competition"]
		tests = self.config["statistics"]["match"]

		data = su.load_match(apikey, competition)
		su.matchloop(apikey, competition, data, tests)

		self.match_ = False

		if self.match_enable == True and self.match_ == False:
			
			task = threading.Thread(name = "match", target = match)
			task.start()

	def metric():

		self.metric_ = True

		apikey = self.config["key"]["database"]
		tbakey = self.config["key"]["tba"]
		competition = self.config["competition"]
		metric = self.config["statistics"]["metric"]

		timestamp = su.get_previous_time(apikey)

		su.metricloop(tbakey, apikey, competition, timestamp, metric)

		self.metric_ = False

		if self.metric_enable == True and self.metric_ == False:
			
			task = threading.Thread(name = "match", target = metric)
			task.start()

	def pit():

		self.pit_ = True

		apikey = self.config["key"]["database"]
		competition = self.config["competition"]
		tests = self.config["statistics"]["pit"]

		data = su.load_pit(apikey, competition)
		su.pitloop(apikey, competition, data, tests)

		self.pit_ = False

		if self.pit_enable == True and self.pit_ == False:
			
			task = threading.Thread(name = "pit", target = pit)
			task.start()

	def start_match():
		task = threading.Thread(name = "match", target = match)
		task.start()

	def start_metric():
		task = threading.Thread(name = "match", target = metric)
		task.start()

	def start_pit():
		task = threading.Thread(name = "pit", target = pit)
		task.start()

	def stop_match():
		self.match_enable = False

	def stop_metric():
		self.metric_enable = False

	def stop_pit():
		self.pit_enable = False

	def get_match():
		return self.match_

	def get_metric():
		return self.metric_

	def get_pit():
		return self.pit_

	def get_match_enable():
		return self.match_enable

	def get_metric_enable():
		return self.metric_enable

	def get_pit_enable():
		return self.pit_enable
"""
def main():

	init()
	start_match()
	start_metric()
	start_pit()

	exit = False
	while(not exit):

		i = input("> ")
		cmds = i.split(" ")
		cmds = [x for x in cmds if x != ""]
		l = len(cmds)

		if(l == 0):
			pass
		else:
			if(cmds[0] == "exit"):
				if(l == 1):
					exit = True
				else:
					print("exit command expected no arguments but encountered " + str(l - 1))
			if(cmds[0] == "status"):
				if(l == 1):
					print("status command expected 1 argument but encountered none\ntype status help for usage")
				elif(l > 2):
					print("status command expected 1 argument but encountered " + str(l - 1))
				elif(cmds[1] == "threads"):
					threads = threading.enumerate()
					threads = [x.getName() for x in threads]
					print("running threads:")
					for thread in threads:
						print("    " + thread)
				elif(cmds[1] == "flags"):
					print("current flags:")
					print("    match running: " + match_)
					print("    metric running: " + metric_)
					print("    pit running: " + pit_)
					print("    match enable: " + match_enable)
					print("    metric enable: " + metric_enable)
					print("    pit enable: " + pit_enable)
				elif(cmds[1] == "config"):
					print("current config:")
					print(json.dumps(config))
				elif(cmds[1] == "all"):
					threads = threading.enumerate()
					threads = [x.getName() for x in threads]
					print("running threads:")
					for thread in threads:
						print("    " + thread)
					print("current flags:")
					print("    match running: " + match_)
					print("    metric running: " + metric_)
					print("    pit running: " + pit_)
					print("    match enable: " + match_enable)
					print("    metric enable: " + metric_enable)
					print("    pit enable: " + pit_enable)
				elif(cmds[1] == "help"):
					print("usage: status [arg]\nDisplays the status of the tra data analysis threads.\nArguments:\n    threads - prints the stuatus ofcurrently running threads\n    flags - prints the status of control and indicator flags\n    config - prints the current configuration information\n    all - prints all statuses\n    <name_of_thread> - prints the status of a specific thread")
				else:
					threads = threading.enumerate()
					threads = [x.getName() for x in threads]
					if(cmds[1] in threads):
						print(cmds[1] + " is running")
				
if(__name__ == "__main__"):
	main()
"""