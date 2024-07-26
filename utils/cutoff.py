import pandas as pd
import numpy as np
import json
from crawler import preprocess_data
import pickle

filePath = './../cutoff.txt'

with open('carbonfree.json') as f:
    data = json.load(f)

data = preprocess_data(data)

df = pd.DataFrame([(website, detail_id, detail_data['css'], detail_data['fetch'], detail_data['g of CO2'], detail_data['img'], detail_data['link'], detail_data['script'], detail_data['video'])
                   for website, details in data.items()
                   for detail_id, detail_data in details.items()],
                  columns=['Website', 'Detail ID', 'CSS', 'Fetch', 'CO2', 'Img', 'Link', 'Script', 'Video'])

filtered_df = df[df['CO2'] != 0]

# 백분율 값을 0에서 100 사이의 값으로 변환
percentiles = [0, 5, 10, 20, 30, 50, 100]
percentile_values = [p / 100 for p in percentiles]

# CO2를 기준으로 데이터프레임 정렬
sorted_df = filtered_df.sort_values(by='CO2')

# 데이터셋을 나눌 백분위수 계산
percentile_values = sorted_df['CO2'].quantile(percentile_values).tolist()

# 각 구간에 속하는 데이터를 분할
carbon_upper_bound = []
for i in range(len(percentile_values) - 1):
    lower_bound = percentile_values[i]
    upper_bound = percentile_values[i + 1]
    carbon_upper_bound.append(upper_bound)

with open(filePath, 'wb') as lf:
    pickle.dump(carbon_upper_bound, lf)

with open(filePath, 'rb') as lf:
    readList = pickle.load(lf)
    print(readList)