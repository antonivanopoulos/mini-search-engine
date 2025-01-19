from pathlib import Path

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import yaml

from crawler.items import DocumentItem

class MainSpider(CrawlSpider):
    name = "main"
    allowed_domains = []
    start_urls = []

    rules = (
      Rule(
          LinkExtractor(deny=('\.phar', '\.pdf')),
          callback="parse_item",
          follow=True,
      ),
    )

    allowed_domains = []
    start_urls = []

    def __init__(self, *args, **kwargs):
      super(MainSpider, self).__init__(*args, **kwargs)

      config_path = Path("config/domains.yml")

      if config_path.is_file():
        with open(config_path, "r") as file:
          config = yaml.safe_load(file)
          domains = config["domains"]

          self.allowed_domains = [allowed_domain for domain in domains for allowed_domain in domain["allowed_domains"]]
          self.start_urls = [domain["start_url"] for domain in domains]

    def parse_item(self, response):
      domain = response.url.split("/")[2]

      item = DocumentItem()
      item['url'] = response.url
      item['domain'] = domain
      item['html_content'] = response.text

      yield item
