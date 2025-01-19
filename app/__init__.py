import os

from flask import Flask

from .routes import search_engine_blueprint

def create_app(index_handler, document_store):
  app = Flask(__name__)
  app.register_blueprint(search_engine_blueprint)

  app.config["INDEX_HANDLER"] = index_handler
  app.config["DOCUMENT_STORE"] = document_store

  return app