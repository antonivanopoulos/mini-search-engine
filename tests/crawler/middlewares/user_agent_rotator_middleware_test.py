import unittest
from unittest.mock import MagicMock, patch
from crawler.crawler.middlewares.user_agent_rotator_middleware import UserAgentRotatorMiddleware  # Replace 'your_module' with the actual module name

class TestUserAgentRotatorMiddleware(unittest.TestCase):
  def setUp(self):
    self.user_agents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
      'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
      'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
    ]
    self.middleware = UserAgentRotatorMiddleware(self.user_agents)

  @patch("random.choice")
  def test_process_request_sets_random_user_agent(self, mock_random_choice):
    mock_random_choice.return_value = self.user_agents[0]

    request_mock = MagicMock()
    spider_mock = MagicMock()

    self.middleware.process_request(request_mock, spider_mock)

    # Ensure the chosen User-Agent is set in the request headers
    self.assertEqual(request_mock.headers['User-Agent'], self.user_agents[0])
    mock_random_choice.assert_called_with(self.user_agents)

  def test_from_crawler(self):
    crawler_mock = MagicMock()
    crawler_mock.settings.get.return_value = self.user_agents

    middleware = UserAgentRotatorMiddleware.from_crawler(crawler_mock)

    # Ensure the middleware is initialized with the correct user agents
    self.assertEqual(middleware.user_agents, self.user_agents)
    crawler_mock.settings.get.assert_called_with('USER_AGENTS', [])

if __name__ == "__main__":
  unittest.main()