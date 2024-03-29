# contains deprecated functions, not to be used unless nessasary!

import json

sample_json = """
{
   "persistent":{
      "key":{
         "database":"",
         "tba":"",
         "tra":{
            "CLIENT_ID":"",
            "CLIENT_SECRET":"",
			"url": ""
         }
      },
      "config-preference":"local",
      "synchronize-config":false
   },
   "variable":{
      "max-threads":0.5,
      "team":"",
      "event-delay":false,
      "loop-delay":0,
      "reportable":true,
      "teams":[
         
      ],
      "modules":{
         "match":{
            "tests":{
               "balls-blocked":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-collected":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-lower-teleop":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-lower-auto":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-started":[
                  "basic_stats",
                  "historical_analyss",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-upper-teleop":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-upper-auto":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ]
            }
         },
         "metric":{
            "tests":{
               "gl2":{
                  "score":1500,
                  "rd":250,
                  "vol":0.06
               },
            }
         },
         "pit":{
            "tests":{
               "wheel-mechanism":true,
               "low-balls":true,
               "high-balls":true,
               "wheel-success":true,
               "strategic-focus":true,
               "climb-mechanism":true,
               "attitude":true
            }
         }
      }
   }
}
"""

def load_config(path, config_vector):
	try:
		f = open(path, "r")
		config_vector.update(json.load(f))
		f.close()
		return 0
	except:
		f = open(path, "w")
		f.write(sample_json)
		f.close()
		return 1