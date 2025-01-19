## Installation
To install all of the dependencies, just run:
```
pip install -r requirements.txt
```
## Architecture
See [ARCHITECTURE](docs/ARCHITECTURE.md)
## Crawling and Indexing
Things are a little manual at the moment in regards to how data is ingested and made available to the search engine interface.
### Crawling
The application uses Scrapy to crawl through the list of configured domains. To run the crawler, you can run the following:
```
$ cd crawler
$ scrapy crawl main
```

If you want to run the crawler with the debug logs enabled (the default level is INFO), you can run the following:

```
$ scrapy crawl main --loglevel DEBUG
```

The default domain page limit is 1000, this can be tweaked in `crawler/crawler/settings.py` if you want to crawl a smaller subset of pages per domain.

The crawler also makes use of Scrapy's checkpointing feature, so you can interrupt it at anytime and continue on from where it left off later.
## Indexing
Once the crawler has done or been cut short, you can run the indexing script to ETL some of the crawled data into a Tantivy index using a relatively slim schema. To do this, you can run (from the root directory):
```
$ python indexer/indexer.py
```
## Tests
You can run the suite of unit tests using PyTest:
```
pytest tests
```

## Deployment
See [DEPLOYMENT](docs/DEPLOYMENT.md)