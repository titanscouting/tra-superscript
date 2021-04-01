# Red Alliance Analysis &middot; ![GitHub release (latest by date)](https://img.shields.io/github/v/release/titanscout2022/red-alliance-analysis)

Titan Robotics 2022 Strategy Team Repository for Data Analysis Tools. Included with these tools are the backend data analysis engine formatted as a python package, associated binaries for the analysis package, and premade scripts that can be pulled directly from this repository and will integrate with other Red Alliance applications to quickly deploy FRC scouting tools.

---

# `data-analysis`

To facilitate data analysis of collected scouting data in a user firendly tool, we created the data-analysis application. At its core it uses the tra-analysis package to conduct any number of user selected tests on data collected from the TRA scouting app. It uploads these tests back to MongoDB where it can be viewed from the app at any time.  

The data-analysis application also uses the TRA API to interface with MongoDB and uses the TBA API to collect additional data (match win/loss).

The application can be configured with a configuration tool or by editing the config.json directly.

## Prerequisites

---

Before installing and using data-analysis, make sure that you have installed the folowing prerequisites:
- A common operating system like **Windows** or (*most*) distributions of **Linux**. BSD may work but has not been tested nor is it reccomended.
- [Python](https://www.python.org/) version **3.6** or higher
- [Pip](https://pip.pypa.io/en/stable/) (installation instructions [here](https://pip.pypa.io/en/stable/installing/))

## Installing Requirements

---

Once navigated to the data-analysis folder run `pip install -r requirements.txt` to install all of the required python libraries.

## Scripts

---

The data-analysis application is a collection of various scripts and one config file. For users, only the main application `superscript.py` and the config file `config.json` are important. 

To run the data-analysis application, navigate to the data-analysis folder once all requirements have been installed and run `python superscript.py`. If you encounter the error:

`pymongo.errors.ConfigurationError: Empty host (or extra comma in host list).`

don't worry, you may have just not configured the application correctly, but would otherwise work. Refer to [the documentation](https://titanscouting.github.io/analysis/data_analysis/Config) to learn how to configure data-analysis.

---

# Build Statuses

Coming soon!