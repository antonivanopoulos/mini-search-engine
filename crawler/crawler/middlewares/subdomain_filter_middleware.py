import yaml
from scrapy.exceptions import IgnoreRequest
from pathlib import Path
from urllib.parse import urlparse

class SubdomainFilterMiddleware:
  """
  Middleware to filter out irrelevant subdomain pages
  """
  def __init__(self):
    config_path = Path("config/domains.yml")
    self.allowed_domains = []

    if config_path.is_file():
      with open(config_path, "r") as file:
        config = yaml.safe_load(file)
        domains = config["domains"]
        self.allowed_domains = [allowed_domain for domain in domains for allowed_domain in domain["allowed_domains"]]

  def process_request(self, request, spider):
    hostname = urlparse(request.url).hostname

    if hostname and hostname not in self.allowed_domains:
      spider.logger.info(f"Blocked subdomain: {hostname}")
      raise IgnoreRequest(f"Subdomain {hostname} is not allowed")