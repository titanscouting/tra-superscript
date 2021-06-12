import data as d

def get_previous_time(apikey):

	previous_time = d.get_analysis_flags(apikey, "latest_update")

	if previous_time == None:

		d.set_analysis_flags(apikey, "latest_update", 0)
		previous_time = 0

	else:

		previous_time = previous_time["latest_update"]

	return previous_time

def set_current_time(apikey, current_time):

	d.set_analysis_flags(apikey, "latest_update", {"latest_update":current_time})

def load_match(apikey, competition):

	return d.get_match_data_formatted(apikey, competition)

def load_metric(apikey, competition, match, group_name, metrics):

	group = {}

	for team in match[group_name]:

		db_data = d.get_team_metrics_data(apikey, competition, team)

		if d.get_team_metrics_data(apikey, competition, team) == None:

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

	return d.get_pit_data_formatted(apikey, competition)

def push_match(apikey, competition, results):

	for team in results:

		d.push_team_tests_data(apikey, competition, team, results[team])

def push_metric(apikey, competition, metric):

	for team in metric:

			d.push_team_metrics_data(apikey, competition, team, metric[team])

def push_pit(apikey, competition, pit):

	for variable in pit:

		d.push_team_pit_data(apikey, competition, variable, pit[variable])