import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, current_app
from app import create_app

class TestSearchEngineBlueprint(unittest.TestCase):
  def setUp(self):
    app = create_app(MagicMock(), MagicMock())
    self.app = app.test_client()
    self.app_context = app.app_context()
    self.app_context.push()

  def tearDown(self):
    self.app_context.pop()

  def test_home_route(self):
    response = self.app.get("/")
    self.assertEqual(response.status_code, 200)
    self.assertIn(b"Mini Search Engine", response.data)
    self.assertNotIn(b"<div id=\"result-list\">", response.data)
    self.assertIn(b"View Stats", response.data)

  @patch("time.time")
  def test_search_route_with_query(self, mock_time):
    mock_time.side_effect = [1.0, 2.0]

    index_handler = current_app.config['INDEX_HANDLER']
    index_handler.search.return_value = [
      {"url": "http://example.com", "score": 0.9},
      {"url": "http://example.org", "score": 0.8},
    ]

    document_store = current_app.config['DOCUMENT_STORE']
    document_store.get_documents.return_value = [
      {"url": "http://example.com", "title": "Example", "content": "Test content."},
      {"url": "http://example.org", "title": "Example Org", "content": "More content."},
    ]

    response = self.app.get("/search?q=test")

    self.assertEqual(response.status_code, 200)
    self.assertIn(b"test", response.data)
    self.assertIn(b"Example", response.data)
    self.assertIn(b"Example Org", response.data)
    self.assertIn(b"Query Time: 1000.00ms", response.data)

  def test_search_route_without_query(self):
      response = self.app.get("/search")
      self.assertEqual(response.status_code, 400)
      self.assertIn(b"bad request!", response.data)

  def test_stats_route(self):
      document_store = current_app.config['DOCUMENT_STORE']
      document_store.domain_stats.return_value = [
        {"domain": "example.com", "pages_indexed": 10},
        {"domain": "example.org", "pages_indexed": 5}
      ]

      response = self.app.get("/stats")

      self.assertEqual(response.status_code, 200)
      self.assertIn(b"example.com", response.data)
      self.assertIn(b"10", response.data)
      self.assertIn(b"example.org", response.data)
      self.assertIn(b"5", response.data)

if __name__ == "__main__":
  unittest.main()