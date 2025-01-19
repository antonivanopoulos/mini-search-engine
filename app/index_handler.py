from tantivy import Query, Occur
import re

class IndexHandler:
  NUM_RESULTS = 10

  def __init__(self, index):
    self.index = index

  def search(self, query):
    # Make sure we're pointing at the latest commit
    self.index.reload()
    searcher = self.index.searcher()

    phrase_query = self.index.parse_query(self.escape_query(query), ["title", "content"], {"title": 2, "content": 1})
    english_query = Query.term_query(self.index.schema, "language", "en")

    combined_query = Query.boolean_query(
      [
        (Occur.Must, phrase_query)
      ]
    )

    search = searcher.search(combined_query, self.NUM_RESULTS)

    results = []
    for score, address in search.hits:
      doc = searcher.doc(address)
      results.append({
        "score": score,
        "title": doc.get_first("title"),
        "url": doc.get_first("url"),
      })

    return results

  def escape_query(self, query):
    # Remove quoted parts from a query temporarily so that we can leave them as is
    quoted_pattern = re.compile(r'".*?"')
    quoted_parts = quoted_pattern.findall(query)
    query_without_quotes = quoted_pattern.sub("\u0000", query)

    # Escape the rest of the components of the search query
    escaped_phrases = [self.escape_phrase(phrase) for phrase in query_without_quotes.split(" ")]
    escaped_query = " ".join(escaped_phrases)
    for quoted_part in quoted_parts:
      escaped_query = escaped_query.replace("\u0000", quoted_part, 1)

    return escaped_query

  def escape_phrase(self, phrase):
    special_chars = r'+-&|!(){}[]^"~*?:\\/'

    if any(char in special_chars for char in phrase):
      return f'"{phrase}"'

    return phrase
