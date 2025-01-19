import sqlite3
import os
import gzip
from pathlib import Path

dirname = os.path.dirname(__file__)

class SqlitePipeline:
  def open_spider(self, spider):
    database_path = Path(os.environ.get("DATABASE_PATH", os.path.join(dirname, "../../data/crawled_data.db")))

    self.conn = sqlite3.connect(database_path)
    self.cursor = self.conn.cursor()

    self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      url TEXT UNIQUE NOT NULL,
      domain TEXT NOT NULL,
      title TEXT,
      description TEXT,
      content BLOB,
      language TEXT
    )
    """)

    self.cursor.execute("""
    CREATE INDEX IF NOT EXISTS index_documents_on_domain ON documents (domain);
    """)

    self.conn.commit()

  def close_spider(self, spider):
    self.conn.close()

  def process_item(self, item, spider):
    self.cursor.execute("""
        INSERT INTO documents (url, domain, title, content, language)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET content=excluded.content;
    """, (item['url'], item['domain'], item['title'], gzip.compress(item['cleaned_content'].encode('utf-8')), item["language"]))
    self.conn.commit()

    return item