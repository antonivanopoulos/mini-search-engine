import os
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

print(sys.path)

process = CrawlerProcess(settings=get_project_settings())

def run_spider(spider_name):
  process.crawl(spider_name)
  process.start()