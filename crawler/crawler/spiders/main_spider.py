from pathlib import Path

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import re

from crawler.items import DocumentItem

class MainSpider(CrawlSpider):
    name = "main"
    allowed_domains = ["doc.rust-lang.org"]
    start_urls = ["https://doc.rust-lang.org/"]

    rules = (
        Rule(
            LinkExtractor(),
            callback="parse_item",
            follow=True,
        ),
    )

    def parse_item(self, response):
      content = ''.join(response.xpath("//body//text()").getall())
      content = re.sub(r"\s+", " ", content)

      domain = response.url.split("/")[2]

      item = DocumentItem()
      item['url'] = response.url
      item['domain'] = domain
      item['title'] = response.xpath("//title/text()").get()
      item['content'] = content

      yield item
