from utils import crawler
from utils import network_carbon

search_url = "https://www.naver.com"
carbon_g = 0

log, datasize = crawler.get_json_data(search_url)
# carbon_g = network_carbon.annual_carborn(log[-1]["Size"])
# print("log=",log)
print("datasize=",datasize)
# print("carbon_g=",carbon_g)

