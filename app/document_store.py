import sqlite3
import gzip
import threading
import os
import gzip
from pathlib import Path

dirname = os.path.dirname(__file__)

NUM_RESULTS = 10
class DocumentStore:
  _instance = None
  _lock = threading.Lock()

  def __new__(cls, db_path):
    with cls._lock:
      if cls._instance is None:
        cls._instance = super(DocumentStore, cls).__new__(cls)
        cls._instance._initialize(db_path)
    return cls._instance

  def _initialize(self, db_path):
    self.conn = sqlite3.connect(db_path, check_same_thread=False)
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

  def insert_document(self, url, domain, title, description, content, language):
    """ Insert a new document, or ignore if URL already exists """
    try:
      self.cursor.execute("""
          INSERT INTO documents (url, domain, title, description, content, language)
          VALUES (?, ?, ?, ?, ?, ?)
      """, (url, domain, title, description, gzip.compress(content.encode('utf-8')), language))
      self.conn.commit()
    except sqlite3.IntegrityError:
      print(f"Document with URL {url} already exists.")

  def domain_stats(self):
    query = """
    SELECT domain, COUNT(*) AS page_count
    FROM documents
    GROUP BY domain
    ORDER BY 2 DESC;
    """

    self.cursor.execute(query)
    stats = [{"domain": row[0], "pages_indexed": row[1]} for row in self.cursor.fetchall()]

    return stats

  def get_documents(self, urls):
    query = """
    SELECT url, content, title
    FROM documents
    WHERE url IN (%s);
    """ % ','.join('?' for i in urls)

    self.cursor.execute(query, urls)
    documents = [{"url": row[0], "content": gzip.decompress(row[1]).decode('utf-8'), "title": row[2]} for row in self.cursor.fetchall()]

    return documents

  def close_connection(self):
    """ Close the database connection """
    self.conn.close()