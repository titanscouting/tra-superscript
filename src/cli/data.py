import requests
import pull
import pandas as pd

def pull_new_tba_matches(apikey, competition, cutoff):
	api_key= apikey 
	x=requests.get("https://www.thebluealliance.com/api/v3/event/"+competition+"/matches/simple", headers={"X-TBA-Auth-Key":api_key}, verify=False)
	out = []
	for i in x.json():
		if i["actual_time"] != None and i["actual_time"]-cutoff >= 0 and i["comp_level"] == "qm":
			out.append({"match" : i['match_number'], "blue" : list(map(lambda x: int(x[3:]), i['alliances']['blue']['team_keys'])), "red" : list(map(lambda x: int(x[3:]), i['alliances']['red']['team_keys'])), "winner": i["winning_alliance"]})
	return out

def get_team_match_data(client, competition, team_num):
	db = client.data_scouting
	mdata = db.matchdata
	out = {}
	for i in mdata.find({"competition" : competition, "team_scouted": str(team_num)}):
		out[i['match']] = i['data']
	return pd.DataFrame(out)

def get_team_pit_data(client, competition, team_num):
	db = client.data_scouting
	mdata = db.pitdata
	out = {}
	return mdata.find_one({"competition" : competition, "team_scouted": str(team_num)})["data"]

def get_team_metrics_data(client, competition, team_num):
	db = client.data_processing
	mdata = db.team_metrics
	return mdata.find_one({"competition" : competition, "team": team_num})

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
	x=requests.get("https://titanscouting.epochml.org/api/fetchAllTeamNicknamesAtCompetition?competition="+competition)
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
	mdata.replace_one({"competition" : competition, "team": team_num}, {"_id": competition+str(team_num)+"am", "competition" : competition, "team" : team_num, "metrics" : data}, True)

def push_team_pit_data(client, competition, variable, data, dbname = "data_processing", colname = "team_pit"):
	db = client[dbname]
	mdata = db[colname]
	mdata.replace_one({"competition" : competition, "variable": variable}, {"competition" : competition, "variable" : variable, "data" : data}, True)

def get_analysis_flags(client, flag):
	db = client.data_processing
	mdata = db.flags
	return mdata.find_one({flag:{"$exists":True}})

def set_analysis_flags(client, flag, data):
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

			elo = {"score": metrics["elo"]["score"]}
			gl2 = {"score": metrics["gl2"]["score"], "rd": metrics["gl2"]["rd"], "vol": metrics["gl2"]["vol"]}
			ts = {"mu": metrics["ts"]["mu"], "sigma": metrics["ts"]["sigma"]}

			group[team] = {"elo": elo, "gl2": gl2, "ts": ts}

		else:

			metrics = db_data["metrics"]

			elo = metrics["elo"]
			gl2 = metrics["gl2"]
			ts = metrics["ts"]

			group[team] = {"elo": elo, "gl2": gl2, "ts": ts}

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