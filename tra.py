import json
import superscript as su
import threading

__author__ = (
	"Arthur Lu <learthurgo@gmail.com>",
)

match = False
metric = False
pit = False

match_enable = True
metric_enable = True
pit_enable = True

config = {}

def main():

	global match
	global metric
	global pit

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

	match = True

	apikey = config["key"]["database"]
	competition = config["competition"]
	tests = config["statistics"]["match"]

	data = su.load_match(apikey, competition)
	su.matchloop(apikey, competition, data, tests)

	match = False

	if match_enable == True and match == False:
		
		task = threading.Thread(name = "match", target = match)
		task.start()

def metric():

	metric = True

	apikey = config["key"]["database"]
	tbakey = config["key"]["tba"]
	competition = config["competition"]
	metric = config["statistics"]["metric"]

	timestamp = su.get_previous_time(apikey)

	su.metricloop(tbakey, apikey, competition, timestamp, metric)

	metric = False

	if metric_enable == True and metric == False:
		
		task = threading.Thread(name = "match", target = metric)
		task.start()

def pit():

	pit = True

	apikey = config["key"]["database"]
	competition = config["competition"]
	tests = config["statistics"]["pit"]

	data = su.load_pit(apikey, competition)
	su.pitloop(apikey, competition, data, tests)

	pit = False

	if pit_enable == True and pit == False:
		
		task = threading.Thread(name = "pit", target = pit)
		task.start()

task = threading.Thread(name = "main", target=main)
task.start()