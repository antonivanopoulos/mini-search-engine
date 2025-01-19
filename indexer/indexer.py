import sqlite3
import tantivy
import os
import gzip

from pathlib import Path
from pathlib import Path

dirname = os.path.dirname(__file__)

def create_or_open_index(index_path):
  if not index_path.exists():
    print("Index doesn't exist, creating new index")
    return create_index(index_path)
  else:
    print("Opening existing index")
    index = tantivy.Index.open(str(index_path))

  return index

def create_index(index_path):
  schema_builder = tantivy.SchemaBuilder()
  schema_builder.add_text_field("title", stored=True)
  schema_builder.add_text_field("content", stored=False, tokenizer_name='en_stem')
  schema_builder.add_text_field("url", stored=True, tokenizer_name="raw")
  schema_builder.add_text_field("language", stored=False)
  schema = schema_builder.build()

  index_path.mkdir(exist_ok=True)
  index = tantivy.Index(schema, path=str(index_path))
  return index

def index_documents(index, database_path):
  conn = sqlite3.connect(database_path)
  cursor = conn.cursor()

  cursor.execute("SELECT title, content, url, language FROM documents")
  for batch in iter(lambda: cursor.fetchmany(1000), []):
    print("Writing batch")
    writer = index.writer()
    for row in batch:
      if row[0] and row[1] and row[2]:
        # Tantivy doesn't really do updates as atomic operations, we need to delete the existing document using the URL
        # as an "id" and then re-insert it.
        writer.delete_documents(field_name="url", field_value=row[2])
        writer.add_document(
          tantivy.Document(
            title=row[0],
            content=gzip.decompress(row[1]).decode('utf-8'),
            url=row[2],
            language=row[3] or "en"
          )
        )
    writer.commit()
    writer.wait_merging_threads()

  conn.close()
  print(f"Finished indexing")

def main():
  index_path = Path(os.environ.get("INDEX_PATH", os.path.join(dirname, "../data/index")))
  database_path = Path(os.environ.get("DATABASE_PATH", os.path.join(dirname, "../data/crawled_data.db")))

  index = create_or_open_index(index_path)
  index_documents(index, database_path)

if __name__ == "__main__":
  main()
