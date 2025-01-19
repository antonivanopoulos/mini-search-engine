import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import gzip
import os
from pathlib import Path
from crawler.crawler.pipelines.sqlite_pipeline import SqlitePipeline

class TestSqlitePipeline(unittest.TestCase):
    @patch("sqlite3.connect")
    @patch("os.environ.get")
    def test_open_spider_creates_database_and_table(self, mock_get_env, mock_connect):
        mock_get_env.return_value = "/test/path/crawled_data.db"
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        pipeline = SqlitePipeline()
        pipeline.open_spider(None)

        # Check that connect was called with the expected path
        mock_connect.assert_called_with(Path("/test/path/crawled_data.db"))

        # Verify the table creation queries were executed
        mock_connection.cursor.return_value.execute.assert_any_call(
            """
            CREATE TABLE IF NOT EXISTS documents(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              url TEXT UNIQUE NOT NULL,
              domain TEXT NOT NULL,
              title TEXT,
              description TEXT,
              content BLOB,
              language TEXT
            )
            """
        )

        mock_connection.cursor.return_value.execute.assert_any_call(
            """
            CREATE INDEX IF NOT EXISTS index_documents_on_domain ON documents (domain);
            """
        )

        # Verify commit was called
        mock_connection.commit.assert_called()

    @patch("sqlite3.connect")
    def test_close_spider_closes_connection(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        pipeline = SqlitePipeline()
        pipeline.open_spider(None)
        pipeline.close_spider(None)

        # Verify close was called on the connection
        mock_connection.close.assert_called()

    @patch("sqlite3.connect")
    def test_process_item_inserts_data(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        pipeline = SqlitePipeline()
        pipeline.open_spider(None)

        item = {
            "url": "http://example.com",
            "domain": "example.com",
            "title": "Example Title",
            "cleaned_content": "This is some content.",
            "language": "en"
        }

        pipeline.process_item(item, None)

        # Verify the insert query was executed with the correct parameters
        mock_connection.cursor.return_value.execute.assert_called_with(
            """
            INSERT INTO documents (url, domain, title, content, language)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET content=excluded.content;
            """,
            (
                "http://example.com",
                "example.com",
                "Example Title",
                gzip.compress(b"This is some content."),
                "en"
            )
        )

        # Verify commit was called
        mock_connection.commit.assert_called()

    def test_compress_content_gzip(self):
        content = "This is test content."
        compressed_content = gzip.compress(content.encode("utf-8"))

        self.assertEqual(SqlitePipeline.compress_content_gzip(content), compressed_content)

if __name__ == "__main__":
    unittest.main()