import unittest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
from crawler.crawler.pipelines.content_extraction_pipeline import ContentExtractionPipeline

class TestContentExtractionPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = ContentExtractionPipeline()

    def test_process_item_with_complete_html(self):
        item = {
            "url": "http://example.com",
            "html_content": """
            <html lang="en">
                <head><title>Test Page</title></head>
                <body>
                    <main>
                        <h1>Main Content</h1>
                        <p>This is a test paragraph.</p>
                    </main>
                </body>
            </html>
            """
        }

        result = self.pipeline.process_item(item, MagicMock())

        self.assertEqual(result["language"], "en")
        self.assertEqual(result["title"], "Test Page")
        self.assertEqual(result["cleaned_content"], "Main Content This is a test paragraph.")

    def test_process_item_with_missing_title(self):
        item = {
            "url": "http://example.com",
            "html_content": """
            <html lang="en">
                <head></head>
                <body>
                    <main>
                        <h1>Fallback Title</h1>
                        <p>Some content here.</p>
                    </main>
                </body>
            </html>
            """
        }

        result = self.pipeline.process_item(item, MagicMock())

        self.assertEqual(result["language"], "en")
        self.assertEqual(result["title"], "Fallback Title")
        self.assertEqual(result["cleaned_content"], "Fallback Title Some content here.")

    def test_process_item_with_no_main_content(self):
        spider_mock = MagicMock()
        item = {
            "url": "http://example.com",
            "html_content": """
            <html lang="en">
                <head><title>Test Page</title></head>
                <body>
                    <header>Header Content</header>
                    <footer>Footer Content</footer>
                </body>
            </html>
            """
        }

        result = self.pipeline.process_item(item, spider_mock)

        self.assertEqual(result["language"], "en")
        self.assertEqual(result["title"], "Test Page")
        self.assertEqual(result["cleaned_content"], "Header Content")

    def test_process_item_with_boilerplate_removal(self):
        item = {
            "url": "http://example.com",
            "html_content": """
            <html lang="en">
                <head><title>Test Page</title></head>
                <body>
                    <main>
                        <script>console.log("Test Script");</script>
                        <style>.test {color: red;}</style>
                        <h1>Main Content</h1>
                        <p>This is a test paragraph.</p>
                        <footer>Footer Content</footer>
                    </main>
                </body>
            </html>
            """
        }

        result = self.pipeline.process_item(item, MagicMock())

        self.assertEqual(result["language"], "en")
        self.assertEqual(result["title"], "Test Page")
        self.assertEqual(result["cleaned_content"], "Main Content This is a test paragraph.")

if __name__ == "__main__":
    unittest.main()
