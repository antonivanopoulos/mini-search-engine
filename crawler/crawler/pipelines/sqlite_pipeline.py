import sqlite3
import os
import gzip
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.document_store import DocumentStore

dirname = os.path.dirname(__file__)

class SqlitePipeline:
  def open_spider(self, spider):
    dirname = os.path.dirname(__file__)
    database_path = Path(os.environ.get("DATABASE_PATH", os.path.join(dirname, "../../../data/crawled_data.db")))
    self.db = DocumentStore(database_path)

  def close_spider(self, spider):
    self.db.close_connection()

  def process_item(self, item, spider):
    self.db.insert_document(
      url=item['url'],
      domain=item['domain'],
      title=item['title'],
      description=item.get('description'),
      content=item['cleaned_content'],
      language=item.get('language')
    )

    return item