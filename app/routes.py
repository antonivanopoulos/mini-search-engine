from flask import Blueprint, request, render_template, current_app

import time

search_engine_blueprint = Blueprint("routes", __name__)

@search_engine_blueprint.route("/")
def home():
  return render_template("home.html")

@search_engine_blueprint.route("/search")
def search():
  query = request.args.get("q")
  if not query:
    return 'bad request!', 400

  index_handler = current_app.config.get("INDEX_HANDLER")
  document_store = current_app.config.get("DOCUMENT_STORE")

  start = time.time()
  results = index_handler.search(query)
  end = time.time()

  scores = {result["url"]:result["score"] for result in results}
  urls = list(scores.keys())

  # Need to re-order these by the original score
  documents = document_store.get_documents(urls)
  for document in documents:
    document["score"] = scores[document["url"]]

  # Re-sort the returned documents using the original score from highest score to lowest
  sorted_documents = sorted(documents, key=lambda document: document["score"], reverse=True)
  elapsed = end - start

  return render_template('search.html', query=query, results=sorted_documents, elapsed=elapsed)

@search_engine_blueprint.route("/stats")
def stats():
  document_store = current_app.config.get("DOCUMENT_STORE")
  domain_stats = document_store.domain_stats()

  return render_template('stats.html', domain_stats=domain_stats)