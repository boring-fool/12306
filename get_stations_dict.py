import re
import json
import requests

# 获取车站编号字符串
url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9076'
resp = requests.get(url)
stations_str = re.search("'(.*)'", resp.text).group(1)

# 获取{城市(车站):编码, ...} 键值对
stations_dict = {}
for station in stations_str.split('@'):
    if station == '': # 按@切会切出空字符串
        continue
    stations_dict[station.split('|')[1]] = station.split('|')[2]

with open('./utils/stations_dict.py', 'w', encoding='utf8') as f:
    f.write('stations_dict = ')
    json.dump(stations_dict, f, ensure_ascii=False, indent=4)