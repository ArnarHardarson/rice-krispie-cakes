#import pandas as pd
#from api_calls import games_info_multiple
from api_calls import *

#df = games_info_multiple(2007,2008,1)
#df = games_info_scores_multiple(2007,2022,0)
df = games_info_competitor_multiple(2007,2022,0)
df.to_csv('../../data/games_info_competitor_2007_2022.csv')