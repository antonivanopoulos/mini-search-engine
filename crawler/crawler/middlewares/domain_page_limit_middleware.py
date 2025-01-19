from scrapy.exceptions import IgnoreRequest

class DomainPageLimitMiddleware:
  def __init__(self, domain_page_limit):
    self.domain_page_limit = domain_page_limit
    self.page_count = {}
    self.exceeded_domains = set()

  @classmethod
  def from_crawler(cls, crawler):
    return cls(
      domain_page_limit=crawler.settings.getint("DOMAIN_PAGE_LIMIT", 50)
    )

  def process_request(self, request, spider):
    domain = request.url.split("/")[2]

    if domain in self.exceeded_domains:
      raise IgnoreRequest(f"Domain limit exceeded for {domain}")

    self.page_count[domain] = self.page_count.get(domain, 0) + 1
    if self.page_count[domain] > self.domain_page_limit:
      self.exceeded_domains.add(domain)
      raise IgnoreRequest(f"Domain limit exceeded for {domain}")