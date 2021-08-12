import requests
import pymongo
import pandas as pd

def pull_new_tba_matches(apikey, competition, cutoff):
	api_key= apikey 
	x=requests.get("https://www.thebluealliance.com/api/v3/event/"+competition+"/matches/simple", headers={"X-TBA-Auth_Key":api_key})
	out = []
	for i in x.json():
		if i["actual_time"] != None and i["actual_time"]-cutoff >= 0 and i["comp_level"] == "qm":
			out.append({"match" : i['match_number'], "blue" : list(map(lambda x: int(x[3:]), i['alliances']['blue']['team_keys'])), "red" : list(map(lambda x: int(x[3:]), i['alliances']['red']['team_keys'])), "winner": i["winning_alliance"]})
	return out

def get_team_match_data(apikey, competition, team_num):
	client = pymongo.MongoClient(apikey)
	db = client.data_scouting
	mdata = db.matchdata
	out = {}
	for i in mdata.find({"competition" : competition, "team_scouted": team_num}):
		out[i['match']] = i['data']
	return pd.DataFrame(out)

def get_team_pit_data(apikey, competition, team_num):
	client = pymongo.MongoClient(apikey)
	db = client.data_scouting
	mdata = db.pitdata
	out = {}
	return mdata.find_one({"competition" : competition, "team_scouted": team_num})["data"]

def get_team_metrics_data(apikey, competition, team_num):
	client = pymongo.MongoClient(apikey)
	db = client.data_processing
	mdata = db.team_metrics
	return mdata.find_one({"competition" : competition, "team": team_num})

def get_match_data_formatted(apikey, competition):
	client = pymongo.MongoClient(apikey)
	db = client.data_scouting
	mdata = db.teamlist
	x=mdata.find_one({"competition":competition})
	out = {}
	for i in x:
		try:
			out[int(i)] = unkeyify_2l(get_team_match_data(apikey, competition, int(i)).transpose().to_dict())
		except:
			pass
	return out

def get_metrics_data_formatted(apikey, competition):
	client = pymongo.MongoClient(apikey)
	db = client.data_scouting
	mdata = db.teamlist
	x=mdata.find_one({"competition":competition})
	out = {}
	for i in x:
		try:
			out[int(i)] = get_team_metrics_data(apikey, competition, int(i))
		except:
			pass
	return out

def get_pit_data_formatted(apikey, competition):
	client = pymongo.MongoClient(apikey)
	db = client.data_scouting
	mdata = db.teamlist
	x=mdata.find_one({"competition":competition})
	out = {}
	for i in x:
		try:
			out[int(i)] = get_team_pit_data(apikey, competition, int(i))
		except:
			pass
	return out

def get_pit_variable_data(apikey, competition):
	client = pymongo.MongoClient(apikey)
	db = client.data_processing
	mdata = db.team_pit
	out = {}
	return mdata.find()

def get_pit_variable_formatted(apikey, competition):
	temp = get_pit_variable_data(apikey, competition)
	out = {}
	for i in temp:
		out[i["variable"]] = i["data"]
	return out

def push_team_tests_data(apikey, competition, team_num, data, dbname = "data_processing", colname = "team_tests"):
	client = pymongo.MongoClient(apikey)
	db = client[dbname]
	mdata = db[colname]
	mdata.replace_one({"competition" : competition, "team": team_num}, {"_id": competition+str(team_num)+"am", "competition" : competition, "team" : team_num, "data" : data}, True)

def push_team_metrics_data(apikey, competition, team_num, data, dbname = "data_processing", colname = "team_metrics"):
	client = pymongo.MongoClient(apikey)
	db = client[dbname]
	mdata = db[colname]
	mdata.replace_one({"competition" : competition, "team": team_num}, {"_id": competition+str(team_num)+"am", "competition" : competition, "team" : team_num, "metrics" : data}, True)

def push_team_pit_data(apikey, competition, variable, data, dbname = "data_processing", colname = "team_pit"):
	client = pymongo.MongoClient(apikey)
	db = client[dbname]
	mdata = db[colname]
	mdata.replace_one({"competition" : competition, "variable": variable}, {"competition" : competition, "variable" : variable, "data" : data}, True)

def get_analysis_flags(apikey, flag):
	client = pymongo.MongoClient(apikey)
	db = client.data_processing
	mdata = db.flags
	return mdata.find_one({flag:{"$exists":True}})

def set_analysis_flags(apikey, flag, data):
	client = pymongo.MongoClient(apikey)
	db = client.data_processing
	mdata = db.flags
	return mdata.replace_one({flag:{"$exists":True}}, data, True)

def unkeyify_2l(layered_dict):
	out = {}
	for i in layered_dict.keys():
		add = []
		sortkey = []
		for j in layered_dict[i].keys():
			add.append([j,layered_dict[i][j]])
		add.sort(key = lambda x: x[0])
		out[i] = list(map(lambda x: x[1], add))
	return out

def get_previous_time(apikey):

	previous_time = get_analysis_flags(apikey, "latest_update")

	if previous_time == None:

		set_analysis_flags(apikey, "latest_update", 0)
		previous_time = 0

	else:

		previous_time = previous_time["latest_update"]

	return previous_time

def set_current_time(apikey, current_time):

	set_analysis_flags(apikey, "latest_update", {"latest_update":current_time})

def load_match(apikey, competition):

	return get_match_data_formatted(apikey, competition)

def load_metric(apikey, competition, match, group_name, metrics):

	group = {}

	for team in match[group_name]:

		db_data = get_team_metrics_data(apikey, competition, team)

		if get_team_metrics_data(apikey, competition, team) == None:

			elo = {"score": metrics["elo"]["score"]}
			gl2 = {"score": metrics["gl2"]["score"], "rd": metrics["gl2"]["rd"], "vol": metrics["gl2"]["vol"]}
			ts = {"mu": metrics["ts"]["mu"], "sigm+a": metrics["ts"]["sigma"]}

			group[team] = {"elo": elo, "gl2": gl2, "ts": ts}

		else:

			metrics = db_data["metrics"]

			elo = metrics["elo"]
			gl2 = metrics["gl2"]
			ts = metrics["ts"]

			group[team] = {"elo": elo, "gl2": gl2, "ts": ts}

	return group

def load_pit(apikey, competition):

	return get_pit_data_formatted(apikey, competition)

def push_match(apikey, competition, results):

	for team in results:

		push_team_tests_data(apikey, competition, team, results[team])

def push_metric(apikey, competition, metric):

	for team in metric:

		push_team_metrics_data(apikey, competition, team, metric[team])

def push_pit(apikey, competition, pit):

	for variable in pit:

		push_team_pit_data(apikey, competition, variable, pit[variable])