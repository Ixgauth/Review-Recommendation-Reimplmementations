import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests


def intake_data_frame(filename):
	with open(filename) as file:
		data = json.load(file)

	df = pd.DataFrame(data["commits"])
	return df