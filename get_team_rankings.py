import data as d
from analysis import analysis as an
import pymongo
import operator

def load_config(file):
	config_vector = {}
	file = an.load_csv(file)
	for line in file[1:]:
		config_vector[line[0]] = line[1:]

	return (file[0][0], config_vector)

def get_metrics_processed_formatted(apikey, competition):
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

def main():

	apikey = an.load_csv("keys.txt")[0][0]
	tbakey = an.load_csv("keys.txt")[1][0]

	competition, config = load_config("config.csv")

	metrics = get_metrics_processed_formatted(apikey, competition)

	elo = {}
	gl2 = {}

	for team in metrics:

		elo[team] = metrics[team]["metrics"]["elo"]["score"]
		gl2[team] = metrics[team]["metrics"]["gl2"]["score"]

	elo = {k: v for k, v in sorted(elo.items(), key=lambda item: item[1])}
	gl2 = {k: v for k, v in sorted(gl2.items(), key=lambda item: item[1])}

	for team in elo:

		print("teams sorted by elo:")
		print("" + str(team) + " | " + str(elo[team]))

	print("*"*25)

	for team in gl2:

		print("teams sorted by glicko2:")
		print("" + str(team) + " | " + str(gl2[team]))

main()