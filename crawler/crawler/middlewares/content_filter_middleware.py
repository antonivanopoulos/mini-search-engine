from scrapy.exceptions import IgnoreRequest
import os

class ContentFilterMiddleware:
  """
  Middleware to filter out irrelevant pages based on file extensions and content types
  """
  def __init__(self):
    self.allowed_content_types = ["text/html"]
    self.excluded_extensions = [".css", ".js", ".png", ".jpg", ".gif", ".svg", ".woff", ".ttf"]

  def process_response(self, request, response, spider):
    # Check content type
    content_type = response.headers.get("Content-Type", b"").decode("utf-8")
    if not any(ct in content_type for ct in self.allowed_content_types):
      raise IgnoreRequest("Filtered out non-HTML content.")

    # Check URL for excluded extensions
    if any(response.url.endswith(ext) for ext in self.excluded_extensions):
      raise IgnoreRequest("Filtered out non-relevant resource.")

    # Filter out very small pages
    if len(response.body) < int(os.environ.get("MINIMUM_RESPONSE_BODY_SIZE", 200)):
      raise IgnoreRequest("Filtered out small page.")

    return response