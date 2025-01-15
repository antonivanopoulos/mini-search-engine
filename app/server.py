from app import app
from flask import request, render_template

import time
import os
from pathlib import Path

dirname = os.path.dirname(__file__)

INDEX_PATH = Path(os.path.join(dirname, "../indexer/index"))
if not INDEX_PATH.exists():
  raise RuntimeError(f"Index not found at {INDEX_PATH}")

STORE_PATH = Path(os.path.join(dirname, "../data/crawled_data.db"))
if not STORE_PATH.exists():
  raise RuntimeError(f"Document storage not found at {STORE_PATH}")

from .index_handler import IndexHandler
index = IndexHandler(index_path=str(INDEX_PATH))

from .document_store import DocumentStore

@app.route("/")
def home():
  return render_template("home.html")

@app.route("/search")
def search():
  query = request.args.get("q")
  if not query:
    return 'bad request!', 400

  start = time.time()
  results = index.search(query)
  end = time.time()
  elapsed = end - start

  return render_template('search.html', query=query, results=results, elapsed=elapsed)

@app.route("/stats")
def stats():
  domain_stats = DocumentStore.domain_stats(STORE_PATH)

  return render_template('stats.html', domain_stats=domain_stats)