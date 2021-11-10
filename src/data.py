import requests
import pymongo
import pandas as pd
import time

def pull_new_tba_matches(apikey, competition, cutoff):
	api_key= apikey 
	x=requests.get("https://www.thebluealliance.com/api/v3/event/"+competition+"/matches/simple", headers={"X-TBA-Auth_Key":api_key})
	out = []
	for i in x.json():
		if i["actual_time"] != None and i["actual_time"]-cutoff >= 0 and i["comp_level"] == "qm":
			out.append({"match" : i['match_number'], "blue" : list(map(lambda x: int(x[3:]), i['alliances']['blue']['team_keys'])), "red" : list(map(lambda x: int(x[3:]), i['alliances']['red']['team_keys'])), "winner": i["winning_alliance"]})
	return out

def get_team_match_data(apikey, competition, team_num):
	out = requests.get("/api/fetchAllTeamMatchData", headers = {"competition" : competition, "team_scouted" : team_num, "api_key" : apikey}).json()
	return pd.DataFrame(out)

def get_team_pit_data(apikey, competition, team_num):
	return requests.get("/api/fetchAllTeamPitData", headers = {"competition" : competition, "team_scouted" : team_num, "api_key" : apikey}).json()

def get_team_metrics_data(apikey, competition, team_num):
	return requests.get("/api/fetchMetricsData", headers = {"competition" : competition, "team" : team_num, "api_key" : apikey}).json()

def get_match_data_formatted(apikey, competition): #need help with this one
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

def get_metrics_data_formatted(apikey, competition): #need help with this one
	client = pymongo.MongoClient(apikey)
	db = client.data_scouting
	mdata = db.teamlist
	x=mdata.find_one({"competition":competition})
	out = {}
	for i in x:
		try:
			out[int(i)] = d.get_team_metrics_data(apikey, competition, int(i))
		except:
			pass
	return out

def get_pit_data_formatted(apikey, competition): #need help with this one
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
	return requests.get("/api/fetchPitVariableData", headers = {"competition" : competition, "api_key" : apikey}).json()

def get_pit_variable_formatted(apikey, competition):
	temp = get_pit_variable_data(apikey, competition)
	out = {}
	for i in temp:
		out[i["variable"]] = i["data"]
	return out

def push_team_tests_data(apikey, competition, team_num, data):
	requests.post("/api/submitTeamTestsData", headers = {"competition" : competition, "team" : team_num, "api_key" : apikey}, json=data)

def push_team_metrics_data(apikey, competition, team_num, data):
	requests.post("/api/submitTeamMetricsData", headers = {"competition" : competition, "team" : team_num, "api_key" : apikey}, json=data)

def push_team_pit_data(apikey, competition, team_num, data):
	requests.post("/api/submitTeamPitData", headers = {"competition" : competition, "team" : team_num, "api_key" : apikey}, json=data)

def get_analysis_flags(apikey, flag):
	return requests.get("/api/fetchAnalysisFlags", headers = {"flag" : flag, "api_key" : apikey}).json()

def set_analysis_flags(apikey, flag, data):
	requests.post("/api/setAnalysisFlags", headers = {"flag" : flag, "api_key" : apikey}, json=data)

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
