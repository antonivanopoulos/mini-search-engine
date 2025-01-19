from bs4 import BeautifulSoup
import re

class ContentExtractionPipeline:
  """
  Extract and clean main content for indexing.
  """
  def process_item(self, item, spider):
    html_content = item["html_content"]
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract the language
    language = soup.html.get("lang", "")
    item["language"] = language

    # Extract the title
    title = soup.title.string if soup.title else None
    if not title:
      # Fall back to the first <h1> tag if <title> is missing
      h1_tag = soup.find("h1")
      title = h1_tag.get_text(strip=True) if h1_tag else "No Title Found"

    item["title"] = title

    # Extract main content heuristically
    main_content = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"}) or soup.body

    # Remove boilerplate tags
    for tag in main_content.find_all(["script", "style", "nav", "footer", "aside"]):
      tag.decompose()

    # Clean and normalize text
    cleaned_content = main_content.get_text(separator="\n", strip=True)
    cleaned_content = re.sub(r"\s+", " ", cleaned_content)

    # Update item with cleaned data
    item["cleaned_content"] = cleaned_content

    return item