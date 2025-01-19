import os
import sys

from app import create_app
from pathlib import Path

from indexer.indexer import create_or_open_index
from app.document_store import DocumentStore
from app.index_handler import IndexHandler

dirname = os.path.dirname(__file__)

index_path = Path(os.environ.get("INDEX_PATH", os.path.join(dirname, "data/index")))
index = create_or_open_index(index_path)
index_handler = IndexHandler(index)

database_path = Path(os.environ.get("DATABASE_PATH", os.path.join(dirname, "data/crawled_data.db")))
document_store = DocumentStore(database_path)

app = create_app(index_handler, document_store)
