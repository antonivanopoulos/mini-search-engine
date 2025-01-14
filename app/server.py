from app import app
from flask import request, render_template

from pathlib import Path

import time
import app.index_handler as index_handler

INDEX_PATH = Path("/Users/anton/workspace/kagi-project/indexer/index")
if not INDEX_PATH.exists():
  raise RuntimeError(f"Index not found at {INDEX_PATH}")

from .index_handler import IndexHandler
index = IndexHandler(index_path=str(INDEX_PATH))

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
  return render_template('stats.html')