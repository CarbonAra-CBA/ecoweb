# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# 빠르게 데이터를 처리하기 위해 pipeline을 사용할 수 있음 (근데 아직 사용하지 않겠음. IP 밴 당할까봐)
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class CrawlingspiderPipeline:
    def process_item(self, item, spider):
        return item
