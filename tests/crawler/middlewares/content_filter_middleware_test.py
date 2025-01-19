import unittest
import os

from unittest import mock
from unittest.mock import MagicMock
from scrapy.exceptions import IgnoreRequest
from crawler.crawler.middlewares.content_filter_middleware import ContentFilterMiddleware

class TestContentFilterMiddleware(unittest.TestCase):
    def setUp(self):
        self.middleware = ContentFilterMiddleware()

    @mock.patch.dict(os.environ, {"MINIMUM_RESPONSE_BODY_SIZE": "1"}, clear=True)
    def test_process_response_allowed_content_type(self):
        response_mock = MagicMock()
        response_mock.headers = {"Content-Type": b"text/html"}
        response_mock.url = "http://example.com/page.html"
        response_mock.body = b"<html><body>T</body></html>"

        result = self.middleware.process_response(None, response_mock, MagicMock())
        self.assertEqual(result, response_mock)

    def test_process_response_disallowed_content_type(self):
        response_mock = MagicMock()
        response_mock.headers = {"Content-Type": b"application/json"}
        response_mock.url = "http://example.com/page.json"

        with self.assertRaises(IgnoreRequest):
            self.middleware.process_response(None, response_mock, MagicMock())

    def test_process_response_excluded_extension(self):
        response_mock = MagicMock()
        response_mock.headers = {"Content-Type": b"text/html"}
        response_mock.url = "http://example.com/image.png"

        with self.assertRaises(IgnoreRequest):
            self.middleware.process_response(None, response_mock, MagicMock())

    def test_process_response_small_page(self):
        response_mock = MagicMock()
        response_mock.headers = {"Content-Type": b"text/html"}
        response_mock.url = "http://example.com/page.html"
        response_mock.body = b"<html></html>"  # Very small content

        with self.assertRaises(IgnoreRequest):
            self.middleware.process_response(None, response_mock, MagicMock())

    def test_process_response_large_valid_page(self):
        response_mock = MagicMock()
        response_mock.headers = {"Content-Type": b"text/html"}
        response_mock.url = "http://example.com/page.html"
        response_mock.body = b"<html><body>" + b"A" * 1000 + b"</body></html>"  # Large enough content

        result = self.middleware.process_response(None, response_mock, MagicMock())
        self.assertEqual(result, response_mock)

if __name__ == "__main__":
    unittest.main()
