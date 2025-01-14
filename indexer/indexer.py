import sqlite3
import tantivy
from pathlib import Path

DATABASE_PATH = "../data/crawled_data.db"
INDEX_PATH = Path("index")

def fetch_documents_from_db():
  conn = sqlite3.connect(DATABASE_PATH)
  cursor = conn.cursor()

  cursor.execute("SELECT title, content, url FROM documents")
  documents = []
  for batch in iter(lambda: cursor.fetchmany(100), []):
    documents.extend([{"title": row[0], "content": row[1], "url": row[2]} for row in batch])

  conn.close()

  return documents

def create_or_open_index():
  if not INDEX_PATH.exists():
    print("Index doesn't exist, creating new index")
    return create_index()
  else:
    print("Opening existing index")
    index = tantivy.Index.open(str(INDEX_PATH))

  return index

def create_index():
  schema_builder = tantivy.SchemaBuilder()
  schema_builder.add_text_field("title", stored=True)
  schema_builder.add_text_field("content", stored=True, tokenizer_name='en_stem')
  schema_builder.add_text_field("url", stored=True)
  schema = schema_builder.build()

  INDEX_PATH.mkdir(exist_ok=True)
  index = tantivy.Index(schema, path=str(INDEX_PATH))
  return index

def index_documents(index, documents):
  writer = index.writer()

  for doc in documents:
    if doc["title"] and doc["content"] and doc["url"]:
      # Tantivy doesn't really do updates as atomic operations, we need to delete the existing document using the URL
      # as an "id" and then re-insert it.
      writer.delete_documents(field_name="url", field_value=doc["url"])
      writer.add_document(
        tantivy.Document(
          title=doc["title"],
          content=doc["content"],
          url=doc["url"]
        )
      )

  writer.commit()
  print(f"Indexed {len(documents)} documents.")

def main():
  documents = fetch_documents_from_db()
  index = create_or_open_index()
  index_documents(index, documents)

if __name__ == "__main__":
  main()
