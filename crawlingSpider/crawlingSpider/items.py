# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# 드라이버 종료
import scrapy

class trafficItem(scrapy.Item):
    url = scrapy.Field()
    total_size = scrapy.Field()
    script = scrapy.Field()
    image = scrapy.Field()
    media = scrapy.Field()
    css = scrapy.Field()


