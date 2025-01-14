import tantivy

class IndexHandler:
  NUM_RESULTS = 10

  def __init__(self, index_path):
    self.index = tantivy.Index.open(index_path)
    self.searcher = self.index.searcher()

  def search(self, query):
    parsed_query = self.index.parse_query(query, ["content", "title"])
    search = self.searcher.search(parsed_query, self.NUM_RESULTS)

    results = []
    for score, address in search.hits:
      doc = self.searcher.doc(address)
      results.append({
        "score": score,
        "title": doc.get_first("title"),
        "content": doc.get_first("content"),
        "url": doc.get_first("url"),
      })

    return results