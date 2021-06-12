# Titan Robotics Team 2022: Superscript Script
# Written by Arthur Lu, Jacob Levine, and Dev Singh
# Notes:
# setup:

__version__ = "0.9.0"

# changelog should be viewed using print(analysis.__changelog__)
__changelog__ = """changelog:
	0.9.0:
		- moved printing and logging related functions to interface.py (changelog will stay in this file)
		- changed function return files for load_config and save_config to standard C values (0 for success, 1 for error)
		- added local variables for config location
	0.8.6:
		- added proper main function
	0.8.5:
		- added more gradeful KeyboardInterrupt exiting
		- redirected stderr to errorlog.txt
	0.8.4:
		- added better error message for missing config.json
		- added automatic config.json creation
		- added splash text with version and system info
	0.8.3:
		- updated matchloop with new regression format (requires tra_analysis 3.x)
	0.8.2:
		- readded while true to main function
		- added more thread config options
	0.8.1:
		- optimized matchloop further by bypassing GIL
	0.8.0:
		- added multithreading to matchloop
		- tweaked user log
	0.7.0:
		- finished implementing main function
	0.6.2:
		- integrated get_team_rankings.py as get_team_metrics() function
		- integrated visualize_pit.py as graph_pit_histogram() function
	0.6.1:
		- bug fixes with analysis.Metric() calls
		- modified metric functions to use config.json defined default values
	0.6.0:
		- removed main function
		- changed load_config function
		- added save_config function
		- added load_match function
		- renamed simpleloop to matchloop
		- moved simplestats function inside matchloop
		- renamed load_metrics to load_metric
		- renamed metricsloop to metricloop
		- split push to database functions amon push_match, push_metric, push_pit
		- moved
	0.5.2:
		- made changes due to refactoring of analysis
	0.5.1:
		- text fixes
		- removed matplotlib requirement
	0.5.0:
		- improved user interface
	0.4.2:
		- removed unessasary code
	0.4.1:
		- fixed bug where X range for regression was determined before sanitization
		- better sanitized data
	0.4.0:
		- fixed spelling issue in __changelog__
		- addressed nan bug in regression
		- fixed errors on line 335 with metrics calling incorrect key "glicko2"
		- fixed errors in metrics computing 
	0.3.0:
		- added analysis to pit data
	0.2.1:
		- minor stability patches
		- implemented db syncing for timestamps
		- fixed bugs
	0.2.0:
		- finalized testing and small fixes
	0.1.4:
		- finished metrics implement, trueskill is bugged
	0.1.3:
		- working
	0.1.2:
		- started implement of metrics
	0.1.1:
		- cleaned up imports
	0.1.0:
		- tested working, can push to database
	0.0.9:
		- tested working
		- prints out stats for the time being, will push to database later
	0.0.8:
		- added data import
		- removed tba import
		- finished main method
	0.0.7:
		- added load_config
		- optimized simpleloop for readibility
		- added __all__ entries
		- added simplestats engine
		- pending testing
	0.0.6:
		- fixes
	0.0.5:
		- imported pickle
		- created custom database object
	0.0.4:
		- fixed simpleloop to actually return a vector
	0.0.3:
		- added metricsloop which is unfinished
	0.0.2:
		- added simpleloop which is untested until data is provided
	0.0.1:
		- created script
		- added analysis, numba, numpy imports
"""

__author__ = (
	"Arthur Lu <learthurgo@gmail.com>",
	"Jacob Levine <jlevine@imsa.edu>",
)

__all__ = [
	"load_config",
	"save_config",
	"get_previous_time",
	"load_match",
	"matchloop",
	"load_metric",
	"metricloop",
	"load_pit",
	"pitloop",
	"push_match",
	"push_metric",
	"push_pit",
]

# imports:

import json

from cli_interface import splash, log, ERR, INF, stdout, stderr

config_path = "config.json"
sample_json = """{
	"max-threads": 0.5,
	"team": "",
	"competition": "2020ilch",
	"key":{
		"database":"",
		"tba":""
	},
	"statistics":{
		"match":{
			"balls-blocked":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-collected":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-lower-teleop":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-lower-auto":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-started":["basic_stats","historical_analyss","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-upper-teleop":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-upper-auto":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"]

		},
		"metric":{
			"elo":{
				"score":1500,
				"N":400,
				"K":24
			},
			"gl2":{
				"score":1500,
				"rd":250,
				"vol":0.06
			},
			"ts":{
				"mu":25,
				"sigma":8.33
			}
		},
		"pit":{
			"wheel-mechanism":true,
			"low-balls":true,
			"high-balls":true,
			"wheel-success":true,
			"strategic-focus":true,
			"climb-mechanism":true,
			"attitude":true
		}
	}
}"""

def main():

	splash(__version__)

def load_config(path, config_vector):
	try:
		f = open(path, "r")
	except:
		log(stderr, ERR, "could not find config at <" + path + ">, generating blank config and exiting")
		f = open(path, "w")
		f.write(sample_json)
		f.close()
		return 1
	
	config_vector = json.load(f)
	f.close()
	return 0

def save_config(path, config_vector):
	try:
		f = open(path)
		json.dump(config_vector)
		f.close()
		return 0
	except:
		return 1

if __name__ == "__main__":
	main()