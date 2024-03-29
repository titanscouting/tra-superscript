from calendar import c
import requests
import pull
import pandas as pd
import json

def pull_new_tba_matches(apikey, competition, last_match):
	api_key= apikey
	x=requests.get("https://www.thebluealliance.com/api/v3/event/"+competition+"/matches/simple", headers={"X-TBA-Auth-Key":api_key})
	json = x.json()
	out = []
	for i in json:
		if i["actual_time"] != None and i["comp_level"] == "qm" and i["match_number"] > last_match :
			out.append({"match" : i['match_number'], "blue" : list(map(lambda x: int(x[3:]), i['alliances']['blue']['team_keys'])), "red" : list(map(lambda x: int(x[3:]), i['alliances']['red']['team_keys'])), "winner": i["winning_alliance"]})
	out.sort(key=lambda x: x['match'])
	return out

def pull_new_tba_matches_manual(apikey, competition, cutoff):
	filename = competition+"-wins.json"
	with open(filename, 'r') as f:
		data = json.load(f)
		return data

def get_team_match_data(client, competition, team_num):
	db = client.data_scouting
	mdata = db.matchdata
	out = {}
	for i in mdata.find({"competition" : competition, "team_scouted": str(team_num)}):
		out[i['match']] = i['data']
	return pd.DataFrame(out)

def clear_metrics(client, competition):
	db = client.data_processing
	data = db.team_metrics
	data.delete_many({competition: competition})
	return True

def get_team_pit_data(client, competition, team_num):
	db = client.data_scouting
	mdata = db.pitdata
	out = {}
	return mdata.find_one({"competition" : competition, "team_scouted": str(team_num)})["data"]

def get_team_metrics_data(client, competition, team_num):
	db = client.data_processing
	mdata = db.team_metrics
	temp = mdata.find_one({"team": team_num})
	if temp != None:
		if competition in temp['metrics'].keys():
			temp = temp['metrics'][competition]
		else :
			temp = None
	else:
		temp = None
	return temp

def get_match_data_formatted(client, competition):
	teams_at_comp = pull.get_teams_at_competition(competition)
	out = {}
	for team in teams_at_comp:
		try:
			out[int(team)] = unkeyify_2l(get_team_match_data(client, competition, team).transpose().to_dict())
		except:
			pass
	return out

def get_metrics_data_formatted(client, competition):
	teams_at_comp = pull.get_teams_at_competition(competition)
	out = {}
	for team in teams_at_comp:
		try:
			out[int(team)] = get_team_metrics_data(client, competition, int(team))
		except:
			pass
	return out

def get_pit_data_formatted(client, competition):
	x=requests.get("https://scouting.titanrobotics2022.com/api/fetchAllTeamNicknamesAtCompetition?competition="+competition)
	x = x.json()
	x = x['data']
	x = x.keys()
	out = {}
	for i in x:
		try:
			out[int(i)] = get_team_pit_data(client, competition, int(i))
		except:
			pass
	return out

def get_pit_variable_data(client, competition):
	db = client.data_processing
	mdata = db.team_pit
	out = {}
	return mdata.find()

def get_pit_variable_formatted(client, competition):
	temp = get_pit_variable_data(client, competition)
	out = {}
	for i in temp:
		out[i["variable"]] = i["data"]
	return out

def push_team_tests_data(client, competition, team_num, data, dbname = "data_processing", colname = "team_tests"):
	db = client[dbname]
	mdata = db[colname]
	mdata.replace_one({"competition" : competition, "team": team_num}, {"_id": competition+str(team_num)+"am", "competition" : competition, "team" : team_num, "data" : data}, True)

def push_team_metrics_data(client, competition, team_num, data, dbname = "data_processing", colname = "team_metrics"):
	db = client[dbname]
	mdata = db[colname]
	mdata.update_one({"team": team_num}, {"$set": {"metrics.{}".format(competition): data}}, upsert=True)

def push_team_pit_data(client, competition, variable, data, dbname = "data_processing", colname = "team_pit"):
	db = client[dbname]
	mdata = db[colname]
	mdata.replace_one({"competition" : competition, "variable": variable}, {"competition" : competition, "variable" : variable, "data" : data}, True)

def get_analysis_flags(client, flag):
	db = client.data_processing
	mdata = db.flags
	return mdata.find_one({"_id": "2022"})

def set_analysis_flags(client, flag, data):
	db = client.data_processing
	mdata = db.flags
	return mdata.update_one({"_id": "2022"}, {"$set": data})

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

def get_previous_time(client):

	previous_time = get_analysis_flags(client, "latest_update")

	if previous_time == None:

		set_analysis_flags(client, "latest_update", 0)
		previous_time = 0

	else:

		previous_time = previous_time["latest_update"]

	return previous_time

def set_current_time(client, current_time):

	set_analysis_flags(client, "latest_update", {"latest_update":current_time})

def get_database_config(client):

	remote_config = get_analysis_flags(client, "config")
	return remote_config["config"] if remote_config != None else None

def set_database_config(client, config):

	set_analysis_flags(client, "config", {"config": config})

def load_match(client, competition):

	return get_match_data_formatted(client, competition)

def load_metric(client, competition, match, group_name, metrics):

	group = {}

	for team in match[group_name]:

		db_data = get_team_metrics_data(client, competition, team)

		if db_data == None:
			gl2 = {"score": metrics["gl2"]["score"], "rd": metrics["gl2"]["rd"], "vol": metrics["gl2"]["vol"]}

			group[team] = {"gl2": gl2}

		else:

			metrics = db_data

			gl2 = metrics["gl2"]

			group[team] = {"gl2": gl2}

	return group

def load_pit(client, competition):

	return get_pit_data_formatted(client, competition)

def push_match(client, competition, results):

	for team in results:

		push_team_tests_data(client, competition, team, results[team])

def push_metric(client, competition, metric):

	for team in metric:

		push_team_metrics_data(client, competition, team, metric[team])

def push_pit(client, competition, pit):

	for variable in pit:
	
		push_team_pit_data(client, competition, variable, pit[variable])

def check_new_database_matches(client, competition):

	return True
