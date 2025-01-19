import random

class UserAgentRotatorMiddleware:
  def __init__(self, user_agents):
    self.user_agents = user_agents

  @classmethod
  def from_crawler(cls, crawler):
    user_agents = crawler.settings.get('USER_AGENTS', [])
    return cls(user_agents)

  def process_request(self, request, spider):
    user_agent = random.choice(self.user_agents)
    request.headers['User-Agent'] = user_agent