import requests
import pymongo
import pandas as pd
import time

def pull_new_tba_matches(apikey, competition, cutoff):
	api_key= apikey 
	x=requests.get("https://www.thebluealliance.com/api/v3/event/"+competition+"/matches/simple", headers={"X-TBA-Auth_Key":api_key})
	out = []
	for i in x.json():
		if (i["actual_time"] != None and i["actual_time"]-cutoff >= 0 and i["comp_level"] == "qm"):
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