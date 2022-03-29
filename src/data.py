import requests
import pandas as pd
import pymongo
from exceptions import APIError

class Client:

	def __init__(self, config):
		self.competition = config.competition
		self.tbakey = config.tba
		self.mongoclient = pymongo.MongoClient(config.database)
		self.trakey = config.tra

	def close(self):
		self.mongoclient.close()

	def pull_new_tba_matches(self, cutoff):
		competition = self.competition
		api_key= self.tbakey 
		x=requests.get("https://www.thebluealliance.com/api/v3/event/"+competition+"/matches/simple", headers={"X-TBA-Auth-Key":api_key})
		out = []
		for i in x.json():
			if i["actual_time"] != None and i["actual_time"]-cutoff >= 0 and i["comp_level"] == "qm":
				out.append({"match" : i['match_number'], "blue" : list(map(lambda x: int(x[3:]), i['alliances']['blue']['team_keys'])), "red" : list(map(lambda x: int(x[3:]), i['alliances']['red']['team_keys'])), "winner": i["winning_alliance"]})
		return out

	def get_team_match_data(self, team_num):
		client = self.mongoclient
		competition = self.competition
		db = client.data_scouting
		mdata = db.matchdata
		out = {}
		for i in mdata.find({"competition" : competition, "team_scouted": str(team_num)}):
			out[i['match']] = i['data']
		return pd.DataFrame(out)

	def get_team_metrics_data(self, team_num):
		client = self.mongoclient
		competition = self.competition
		db = client.data_processing
		mdata = db.team_metrics
		return mdata.find_one({"competition" : competition, "team": team_num})

	def get_team_pit_data(self, team_num):
		client = self.mongoclient
		competition = self.competition
		db = client.data_scouting
		mdata = db.pitdata
		return mdata.find_one({"competition" : competition, "team_scouted": str(team_num)})["data"]

	def unkeyify_2l(self, layered_dict):
		out = {}
		for i in layered_dict.keys():
			add = []
			sortkey = []
			for j in layered_dict[i].keys():
				add.append([j,layered_dict[i][j]])
			add.sort(key = lambda x: x[0])
			out[i] = list(map(lambda x: x[1], add))
		return out

	def get_match_data_formatted(self):
		teams_at_comp = self.get_teams_at_competition()
		out = {}
		for team in teams_at_comp:
			try:
				out[int(team)] = self.unkeyify_2l(self.get_team_match_data(team).transpose().to_dict())
			except:
				pass	
		return out

	def get_metrics_data_formatted(self):
		competition = self.competition
		teams_at_comp = self.get_teams_at_competition()
		out = {}
		for team in teams_at_comp:
			try:
				out[int(team)] = self.get_team_metrics_data(int(team))
			except:
				pass
		return out

	def get_pit_data_formatted(self):
		client = self.mongoclient
		competition = self.competition
		x=requests.get("https://titanscouting.epochml.org/api/fetchAllTeamNicknamesAtCompetition?competition="+competition)
		x = x.json()
		x = x['data']
		x = x.keys()
		out = {}
		for i in x:
			try:
				out[int(i)] = self.get_team_pit_data(int(i))
			except:
				pass
		return out

	def get_pit_variable_data(self):
		client = self.mongoclient
		db = client.data_processing
		mdata = db.team_pit
		return mdata.find()

	def get_pit_variable_formatted(self):
		temp = self.get_pit_variable_data()
		out = {}
		for i in temp:
			out[i["variable"]] = i["data"]
		return out

	def push_team_tests_data(self, team_num, data, dbname = "data_processing", colname = "team_tests"):
		client = self.mongoclient
		competition = self.competition
		db = client[dbname]
		mdata = db[colname]
		mdata.replace_one({"competition" : competition, "team": team_num}, {"_id": competition+str(team_num)+"am", "competition" : competition, "team" : team_num, "data" : data}, True)

	def push_team_metrics_data(self, team_num, data, dbname = "data_processing", colname = "team_metrics"):
		client = self.mongoclient
		competition = self.competition
		db = client[dbname]
		mdata = db[colname]
		mdata.replace_one({"competition" : competition, "team": team_num}, {"_id": competition+str(team_num)+"am", "competition" : competition, "team" : team_num, "metrics" : data}, True)

	def push_team_pit_data(self, variable, data, dbname = "data_processing", colname = "team_pit"):
		client = self.mongoclient
		competition = self.competition
		db = client[dbname]
		mdata = db[colname]
		mdata.replace_one({"competition" : competition, "variable": variable}, {"competition" : competition, "variable" : variable, "data" : data}, True)

	def get_analysis_flags(self, flag):
		client = self.mongoclient
		db = client.data_processing
		mdata = db.flags
		return mdata.find_one({flag:{"$exists":True}})

	def set_analysis_flags(self, flag, data):
		client = self.mongoclient
		db = client.data_processing
		mdata = db.flags
		return mdata.replace_one({flag:{"$exists":True}}, data, True)

	def get_previous_time(self):

		previous_time = self.get_analysis_flags("latest_update")

		if previous_time == None:

			self.set_analysis_flags("latest_update", 0)
			previous_time = 0

		else:

			previous_time = previous_time["latest_update"]

		return previous_time

	def set_current_time(self, current_time):

		self.set_analysis_flags("latest_update", {"latest_update":current_time})

	def get_database_config(self):

		remote_config = self.get_analysis_flags("config")
		return remote_config["config"] if remote_config != None else None

	def set_database_config(self, config):

		self.set_analysis_flags("config", {"config": config})

	def load_match(self):

		return self.get_match_data_formatted()

	def load_metric(self, match, group_name, metrics):

		group = {}

		for team in match[group_name]:

			db_data = self.get_team_metrics_data(team)

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

	def load_pit(self):

		return self.get_pit_data_formatted()

	def push_match(self, results):

		for team in results:

			self.push_team_tests_data(team, results[team])

	def push_metric(self, metric):

		for team in metric:

			self.push_team_metrics_data(team, metric[team])

	def push_pit(self, pit):

		for variable in pit:
		
			self.push_team_pit_data(variable, pit[variable])

	def check_new_database_matches(self):

		return True

	#----- API implementations below -----#

	def get_team_competition(self):
		trakey = self.trakey
		url = self.trakey['url']
		endpoint = '/api/fetchTeamCompetition'
		params = {
			"CLIENT_ID": trakey['CLIENT_ID'],
			"CLIENT_SECRET": trakey['CLIENT_SECRET']
		}
		response = requests.request("GET", url + endpoint, params=params)
		json = response.json()
		if json['success']:
			return json['competition']
		else:
			raise APIError(json)

	def get_team(self):
		trakey = self.trakey
		url = self.trakey['url']
		endpoint = '/api/fetchTeamCompetition'
		params = {
			"CLIENT_ID": trakey['CLIENT_ID'],
			"CLIENT_SECRET": trakey['CLIENT_SECRET']
		}
		response = requests.request("GET", url + endpoint, params=params)
		json = response.json()
		if json['success']:
			return json['team']
		else:
			raise APIError(json)

	""" doesn't seem to be functional:
	def get_team_match_data(self, team_num):
		trakey = self.trakey
		url = self.trakey['url']
		competition = self.competition
		endpoint = '/api/fetchAllTeamMatchData'
		params = {
			"competition": competition,
			"teamScouted": team_num,
			"CLIENT_ID": trakey['CLIENT_ID'],
			"CLIENT_SECRET": trakey['CLIENT_SECRET']
		}
		response = requests.request("GET", url + endpoint, params=params)
		json = response.json()
		if json['success']:
			return json['data'][team_num]
		else:
			raise APIError(json)"""

	def get_teams_at_competition(self):
		trakey = self.trakey
		url = self.trakey['url']
		competition = self.competition
		endpoint = '/api/fetchAllTeamNicknamesAtCompetition'
		params = {
			"competition": competition,
			"CLIENT_ID": trakey['CLIENT_ID'],
			"CLIENT_SECRET": trakey['CLIENT_SECRET']
		}
		response = requests.request("GET", url + endpoint, params=params)
		json = response.json()
		if json['success']:
			return list(json['data'].keys())
		else:
			raise APIError(json)