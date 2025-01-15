import sqlite3

class DocumentStore:
  NUM_RESULTS = 10

  def domain_stats(store_path):
    conn = sqlite3.connect(store_path)
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