import sqlite3
import gzip

class DocumentStore:
  NUM_RESULTS = 10

  def __init__(self, store_path):
    self.store_path = store_path

  def setup(self):
    conn = sqlite3.connect(str(self.store_path))
    cursor = conn.cursor()

    cursor.execute("""
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

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS index_documents_on_domain ON documents (domain);
    """)

    conn.commit()
    conn.close()

  def domain_stats(self):
    conn = sqlite3.connect(self.store_path)
    cursor = conn.cursor()

    query = """
    SELECT domain, COUNT(*) AS page_count
    FROM documents
    GROUP BY domain;
    """

    cursor.execute(query)
    stats = [{"domain": row[0], "pages_indexed": row[1]} for row in cursor.fetchall()]
    conn.close()

    return stats

  def get_documents(self, urls):
    conn = sqlite3.connect(self.store_path)
    cursor = conn.cursor()

    query = """
    SELECT url, content, title
    FROM documents
    WHERE url IN (%s);
    """ % ','.join('?' for i in urls)

    cursor.execute(query, urls)
    documents = [{"url": row[0], "content": gzip.decompress(row[1]).decode('utf-8'), "title": row[2]} for row in cursor.fetchall()]
    conn.close()

    return documents
