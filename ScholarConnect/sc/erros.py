
import time
import sys
sys.path.append('.')
from sklearn.datasets import make_classification
import pandas as pd
from models import data
import numpy as np
import os
from market.core.models import MarketRegressor
from market.config import MarketConfig
from market.utils.initial_config import initial_configuration
import json

CONFIG_FILE = './check/config.ini'
config = MarketConfig()
config.load_config(CONFIG_FILE)
rng = np.random.default_rng(config.random_seed)
data = pd.read_csv('init_2D.csv')

config.init_price = data['label'].mean()
config.save_config('config.ini')

if not os.path.exists(config.intermediate_file_location):
    loc = os.path.dirname(config.intermediate_file_location) + '/'
    os.makedirs(loc)
X = initial_configuration(
    data, output_path=config.intermediate_file_location)
df = pd.DataFrame()
# Define the config input
df['x'] = X[:,0]
df['y'] = X[:,1]
df['min_rad'] = X[:,-2]
df['max_rad'] = X[:,-1]
df.to_csv('init_radius.csv', index=False)
start_config = X[:, -2:]
y = X[:, -3]
X = X[:, :-3]
model = MarketRegressor(config)

model.fit(rng=rng, X=X, y=y, start_config=start_config)
print(time.time())