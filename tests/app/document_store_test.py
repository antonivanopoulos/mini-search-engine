import unittest
import os
from app.document_store import DocumentStore

class TestDocumentStore(unittest.TestCase):
  def setUp(self):
    dirname = os.path.dirname(__file__)
    db_path = os.path.join(dirname, "../support/document_store.db")

    self.db = DocumentStore(db_path)
    self.db.cursor.execute("DELETE FROM documents")

  def test_insert_document(self):
    self.db.insert_document("http://example.com", "example.com", "Example", "Description", "Content", "en")
    result = self.db.domain_stats()
    self.assertEqual(result[0], {"domain": "example.com", "pages_indexed":1})

  def test_domain_stats(self):
    self.db.insert_document("http://example.com", "example.com", "Example", "Description", "Content", "en")
    self.db.insert_document("http://example.com/test", "example.com", "Example", "Description", "Content", "en")
    self.db.insert_document("http://otherexample.com", "otherexample.com", "Example", "Description", "Content", "en")
    result = self.db.domain_stats()
    self.assertEqual(len(result), 2)
    self.assertEqual(result[0], {"domain": "example.com", "pages_indexed":2})
    self.assertEqual(result[1], {"domain": "otherexample.com", "pages_indexed":1})

  def test_get_documents(self):
    self.db.insert_document("http://example.com", "example.com", "Example", "Description", "Content", "en")
    self.db.insert_document("http://example.com/test", "example.com", "Example", "Description", "Content", "en")
    self.db.insert_document("http://otherexample.com", "otherexample.com", "Example", "Description", "Content", "en")
    result = self.db.get_documents(["http://example.com/test", "http://otherexample.com"])
    result_urls = [item["url"] for item in result]
    self.assertEqual(len(result_urls), 2)
    self.assertEqual(result_urls[0], "http://example.com/test")
    self.assertEqual(result_urls[1], "http://otherexample.com")

if __name__ == "__main__":
  unittest.main()