# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import matplotlib.pyplot as plt
import data as d
import pymongo


# %%
def get_pit_variable_data(apikey, competition):
	client = pymongo.MongoClient(apikey)
	db = client.data_processing
	mdata = db.team_pit
	out = {}
	return mdata.find()


# %%
def get_pit_variable_formatted(apikey, competition):
	temp = get_pit_variable_data(apikey, competition)
	out = {}
	for i in temp:
		out[i["variable"]] = i["data"]
	return out


# %%
pit = get_pit_variable_formatted("mongodb+srv://api-user-new:titanscout2022@2022-scouting-4vfuu.mongodb.net/test?authSource=admin&replicaSet=2022-scouting-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true", "2020ilch")


# %%
import matplotlib.pyplot as plt
import numpy as np


# %%
fig, ax = plt.subplots(1, len(pit), sharey=True, figsize=(80,15))

i = 0

for variable in pit:

	ax[i].hist(pit[variable])
	ax[i].invert_xaxis()

	ax[i].set_xlabel('')
	ax[i].set_ylabel('Frequency')
	ax[i].set_title(variable)

	plt.yticks(np.arange(len(pit[variable])))

	i+=1

plt.show()


# %%


