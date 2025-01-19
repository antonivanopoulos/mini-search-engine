from scrapy.exceptions import IgnoreRequest
from pathlib import Path
import yaml
import os
import sqlite3
import sys
import tldextract

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.document_store import DocumentStore

class DomainPageLimitMiddleware:
  def __init__(self, domain_page_limit):
    self.domain_page_limit = domain_page_limit
    self.allowed_domains = []
    self.page_count = {}
    self.exceeded_domains = set()

    # Establish the base page count using the configured domains
    config_path = Path("../config/domains.yml")
    if config_path.is_file():
      with open(config_path, "r") as file:
        config = yaml.safe_load(file)

        for domain in config["domains"]:
          self.page_count[domain] = 0

    # Establish the base page count using already processed pages
    dirname = os.path.dirname(__file__)
    database_path = Path(os.environ.get("DATABASE_PATH", os.path.join(dirname, "../../../data/crawled_data.db")))
    document_store = DocumentStore(database_path)
    stats = document_store.domain_stats()
    for domain in stats:
      self.page_count[domain["domain"]] = domain["pages_indexed"]
      if self.page_count[domain["domain"]] > self.domain_page_limit:
        self.exceeded_domains.add(domain["domain"])

  @classmethod
  def from_crawler(cls, crawler):
    return cls(
      domain_page_limit=crawler.settings.getint("DOMAIN_PAGE_LIMIT", 50)
    )

  def process_request(self, request, spider):
    extracted = tldextract.extract(request.url)
    domain = f"{extracted.domain}.{extracted.suffix}"

    if domain in self.exceeded_domains:
      raise IgnoreRequest(f"Domain limit exceeded for {domain}")

    self.page_count[domain] = self.page_count.get(domain, 0) + 1
    if self.page_count[domain] > self.domain_page_limit:
      self.exceeded_domains.add(domain)
      raise IgnoreRequest(f"Domain limit exceeded for {domain}")
