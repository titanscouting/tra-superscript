import json
import superscript as su
import threading

__author__ = (
	"Arthur Lu <learthurgo@gmail.com>",
)

match_ = False
metric_ = False
pit_ = False

match_enable = True
metric_enable = True
pit_enable = True

config = {}

def main():

	global match_
	global metric_
	global pit_

	global match_enable
	global metric_enable
	global pit_enable

	global config
	config = su.load_config("config.json")

	task = threading.Thread(name = "match", target = match)
	task.start()
	task = threading.Thread(name = "match", target = metric)
	task.start()
	task = threading.Thread(name = "pit", target = pit)
	task.start()

def match():

	match_ = True

	apikey = config["key"]["database"]
	competition = config["competition"]
	tests = config["statistics"]["match"]

	data = su.load_match(apikey, competition)
	su.matchloop(apikey, competition, data, tests)

	match_ = False

	if match_enable == True and match_ == False:
		
		task = threading.Thread(name = "match", target = match)
		task.start()

def metric():

	metric_ = True

	apikey = config["key"]["database"]
	tbakey = config["key"]["tba"]
	competition = config["competition"]
	metric = config["statistics"]["metric"]

	timestamp = su.get_previous_time(apikey)

	su.metricloop(tbakey, apikey, competition, timestamp, metric)

	metric_ = False

	if metric_enable == True and metric_ == False:
		
		task = threading.Thread(name = "match", target = metric)
		task.start()

def pit():

	pit_ = True

	apikey = config["key"]["database"]
	competition = config["competition"]
	tests = config["statistics"]["pit"]

	data = su.load_pit(apikey, competition)
	su.pitloop(apikey, competition, data, tests)

	pit_ = False

	if pit_enable == True and pit_ == False:
		
		task = threading.Thread(name = "pit", target = pit)
		task.start()

task = threading.Thread(name = "main", target=main)
task.start()