# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DocumentItem(scrapy.Item):
    url = scrapy.Field()
    domain = scrapy.Field()
    title = scrapy.Field()
    html_content = scrapy.Field()
    cleaned_content = scrapy.Field()
    last_updated = scrapy.Field()
    language = scrapy.Field()
