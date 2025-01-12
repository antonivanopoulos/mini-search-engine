# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3

from itemadapter import ItemAdapter

class SqlitePipeline:
  def open_spider(self, spider):
    self.conn = sqlite3.connect("output/crawled_data.db")
    self.cursor = self.conn.cursor()

    self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      url TEXT UNIQUE NOT NULL,
      domain TEXT NOT NULL,
      title TEXT,
      description TEXT,
      content TEXT
    )
    """)

    self.cursor.execute("""
    CREATE INDEX IF NOT EXISTS index_documents_on_domain ON documents (domain);
    """)

    self.conn.commit()

  def close_spider(self, spider):
    self.conn.close()

  def process_item(self, item, spider):
    try:
      self.cursor.execute("""
          INSERT INTO documents (url, domain, title, content)
          VALUES (?, ?, ?, ?)
      """, (item['url'], item['domain'], item['title'], item['content']))
      self.conn.commit()
    except sqlite3.IntegrityError:
      spider.logger.warning(f"Duplicate entry skipped for URL: {item['url']}")
    return item
