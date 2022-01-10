import requests 
import json
from exceptions import APIError

def load_config(path):
  with open(path, "r") as f:
    return json.load(f)

url = "https://titanscouting.epochml.org"
config_tra = load_config("config.json")
trakey = config_tra['persistent']['key']['tra']

def get_team_competition():
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
    raise APIError(json, endpoint)

def get_team():
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
    raise APIError(json, endpoint)

def get_team_match_data(competition, team_num):
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
    raise APIError(json, endpoint)

def get_teams_at_competition(competition):
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
      raise APIError(json, endpoint)