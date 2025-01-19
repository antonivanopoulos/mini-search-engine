# Architecture

## Technical Stack and Application Structure
I chose to use Python as the language for this project. It's not exactly my most comfortable language to work in, but I know that the ecosystem for projects like this is quite mature and there's a lot of tooling that I was vaguely familiar with, so it made sense as a good starting point. That plus the fact that Tantivy (the index option I ended up going with) had maintained and up-to-date Python bindings meant that I could stick with the one language for the whole system and keep things relatively cohesive.

## Crawler
This search engine uses Scrapy as the crawler implementation that manages the crawling of our provided domain list and the scraping and processing of the html content that is the basis for our search index.

I chose Scrapy because it's a mature and well-documented Python-based web crawling framework. The built-in features and robust ecosystem mean that we can efficiently deal with some of the challenges that come with web crawling at any sort of scale without having to re-invent too much of the wheel, and we can instead focus on solutions to more complex challenges.

It became clear as I progressed with the project that the crawler would produce the bulk of the challenges as it's the system component dealing with a lot of variation in content and structure and trying to massage that into a uniform schema.

### Storage
I use Sqlite as an intermediary storage point of the crawler output before it gets ingested by the indexing module to be stored in the Tantivy index. The tooling gives me a way of exploring the crawled data and make some choices about things to change as part of the holistic search experience and identifying potential problems that might come up in the indexing.

Because I also use the database as the source for the snippet to display per search result and the stats per indexed domain, having a database that I can keep persisted and maintained was important for me rather than using file output. I think Redis would have been a valid alternative for this (particularly if I had started to explore more options in distributed crawling), but I wanted to try and keep the number of dependencies to a minimum for this small-scale project.

**Requirement: Crawler should stay within the provided subdomain/domain/path restrictions**
Scapy provides built-in support for start urls and allowed domains. I've provided a configuration file (crawler/config/domains.yml) that contains our domain restrictions and our spider uses that to restrict what pages we crawl.

**Requirement: No more than 10,000 pages should be indexed from any single domain.**
The implementation of our spider comes with an additional middleware that tracks pages crawled per domain and will cap it at a defined value (in our case, 10000 pages)

Some assumptions have been made here in how we treat the limit per domain:
- Subdomains page counts are aggregated under the root domain.
- Separate TLDs are treated as separate domains unless one explicitly redirects to the other (for example, the URL https://angular.io will redirect to https://angular.dev, however the URL https://v17.angular.io/docs does _not_ redirect and allows the user to browse docs specific to that version).

**Challenge: Redirecting to a different domain given an initial allowed domain**
Following from the above example, angular.io was one of the domains provided in the original scope of domains to crawl, however because the home permanently redirects, a choice must be made as to whether the new domain, angular.dev, should be included in the scope. I've opted to include it (and others like this case) in the scope of crawled domains for the purpose of this exercise.

**Non-Requirement: Javascript rendering is not needed**
This project doesn't implement any sort of Javascript rendering for dynamic content, but it could be done using something like Selenium or Playwright (at the tradeoff of more intensive scraping being performed).

**Non-Requirement: Proxy use is not needed**
This project doesn't require proxy use to be implemented. This means that the crawler is a little more prone to being met with throttling or rate-limiting responses from the server and it just has to wait that out.

However, we could implement this pretty easily by providing a list of proxies and adding another Scrapy middleware that assigns a random proxy to each request. This implementation could become more sophisticated over time if we wanted to track number of uses of that proxy per domain in a window of time, and whether or not that proxy might be considered banned by the server (if the proxy last received a 429 and that was received recently).

**Challenge: Balancing politeness with speed and efficiency of crawling**
There's 166 domains in the provided list, assuming they all hit the cap of 10000 pages then that has means at most crawling and indexing 1.6 million pages. One of my initial worries with that was the total time it would require to do a full crawl.

Scrapy provides a few different levers for assisting with this, by allowing you to specify a maximum number of concurrent requests, and a separate maximum per domain. This, plus the configuration around automatically throttling based on rate limiting responses or throttling, allows us to try and strike a balance between speed on crawling the required pages, and being a good internet citizen.

The project doesn't currently make use of any process-based parallelisation and doesn't have as much throughput as I would like (hovering between 150 - 300 pages / min). I think if I were to think about further optimisations, it would be to batch the list of domains into shards that separate processes could crawl at the same time. It would have to be a consideration of whether SQLite remains the most optimum storage choice in that instance or if we move to a shared store that was more optimised for writes from multiple processes.

The crawler makes use of Scrapy's built-in HTTP cache for recalling pages it's already crawled recently rather than hitting them again.

**Challenge: Optimising crawler output disk size**
Because we're storing a significant amount of content per page in our crawler output, I chose to use gzip to compress the content column before inserting it into the database, then uncompressing it when it gets pulled out by the indexer to add the document to the index.

**Challenge: Scraping relevant content areas**
One of the things that became immediately apparent was the great variety in content structures and hierarchies all these different domains would use in their designs. The challenge here became finding something that worked well enough for most pages that the spider came across without ingesting a bunch of irrelevant or repeated content (things like navigation components or footers).

I used Python's BeautifulSoup library to try and identify the most relevant content block, falling back to the main body tag if none could be found. There's still edge cases and things that don't work quite as well, `frame` elements used on the Java doc pages for example are something the script doesn't pick up.

**Challenge: Dealing with duplicate content**
This was something that the current crawler doesn't have a solution for. But I noticed that a number of pages have similar content but different URLs. I don't know if this ends up as an indexing problem or a crawling problem (or both), but reading up about approaches, it seems like hashing the content is one approach.

I think it depends on what's deemed as "duplicate". For example, the Rust Nightly docs have a similar title and content to the regular docs, just a different URL path, because they're talking about the same packages.

## Indexer
For the purposes of this project, I've chosen Tantivy as the indexer over Vespa.

The choice largely comes down to the ease of use of Tantivy for the scale of this project. It's something we can set up with minimal effort, embed into our project and get it running in production in our single node setup. Because we're using Python for our crawler and for our web app, we can roll this altogether given that Tantivy has some Python bindings as well that we can install with minimal dependencies (we just need to install Rust in our container as a dependency of Tantivy itself). The tool seems to be well optimised, and while it suffers from some potential availability issues because it's limited to running on one node, I only have one node in production anyway so that's not really an issue right now.

As a contrast, Vespa seems to be an extremely powerful, but complicated, tool that's optimised for very large datasets. It's distributed in nature and has a lot of advanced features, but that brings complexity in both learning how to use the tool and deploy it and the cost in managing that infrastructure that might end up being overkill with what I'm trying to achieve here. That distributed nature might also introduce enough latency that our requirement of staying under 50ms might not be achievable, but that's just me theorising and not something I've got evidence for.

**Requirement: The maximum allowable search latency is 50ms.**
Originally when I was iterating on the interface and the index, I had a schema that was comprised of `title`, `url` and `content` fields (and eventually `language`) and I was storing all of them. That storing of the content itself meant that the index was growing at a much faster pace and that was impacting the search latency to the point it went over the maximum allowed latency of 50ms.

What I've done in the current version is to _not_ store the `content` field, but allow it to be searched and tokenised. The reasoning here is that I already have the content itself stored in the crawler output, so I can fetch it from there given the results from the index search. I did have to add an extra step where I merge the original scores back into the results returned from Sqlite and resort them, but that's not too much of an overhead given the 10 results.

**Challenge: Optimising ranking for high relevancy**
To achieve high relevancy in search results, I focused on combining field-based weighting, query expansion, and performance optimisation. Tantivy has native support for BM25 ranking and that provided foundation for ranking documents effectively.

**Challenge: Dealing with foreign language content**
One thing I noticed as my crawler started to hit links that were translations of other pages (the Rust docs are an example here) was that those pages would filter into results. I didn't want to take an approach of just not indexing those pages at all, but I, as an english speaker, would probably want english results where possible.

The approach I took here was to revisit the extraction of content so that I now also pulled out the `lang` attribute on the `html` tag of the document and stored that so it could be a part of the index. With the new `language` field in the index, I could filter out anything that wasn't english using a BooleanQuery in Tantivy that flagged we were interested in `en` language documents in addition to the PhraseQuery parsed from the user submission. You might ask how that's any different from just excluding non-english content from the index entirely, but I see this is a shorter leap towards doing some sort of sensible inferring of the submitted query to decide what language results to include.

This wasn't foolproof as I ran across a number of Swedish or Russian language sites marking themselves as english language.

**Challenge: Handle queries with special characters**
Tantivy requires some escaping of special characters before strings are passed through to the query parser. That's easy enough, but I also wanted to account for cases where a user might have predefined the literals they wanted to pass through, i.e. submitting a query like `rust "std::io"` or something like that.

The index handler does a little pass through of the submitted query and extracts already-quoted segments and then escapes the rest before plugging everything back together and submitting for parsing and searching the index.

**Challenge: A more automated and incremental crawler-to-index pipeline**
A sharp edge of this current implementation is around the all-or-nothing, and manual,  approach to crawling and indexing. A major improvement from this point would be to look at implementing a more incremental crawling, updating and re-indexing of content, rather than crawling everything, and then running a script then re-index everything from that database, regardless of whether or not it's changed. This might need to include an addition to the database that tracks the last time a page was crawled, a hash of the content, and a timestamp of the last time it changed. We might also need to track the last time a page was indexed.

In regards to automation, I think this could be done through something like Celery or a more sophisticated workflow orchestration system like Airflow. I think this particular piece of work coincides with any decisions regarding optimisations around splitting the crawler into processes as well, as perhaps each batch of domains being crawled by a shard could then initiate the indexer on the new round of changes.

## Interface
The web application that acts as an interface for searching our index is written using Flask, a lightweight Python-based web application framework. Our interface is relatively lightweight with three different pages, so this choice makes sense for us to get up and running without too much fuss.

There are three pages available:
- The home page, which makes the search front and centre to the user.
- The search results page, listing out a maximum of 10 results based on the provided search terms.
- The stats page, which lists out the number of pages indexed per domain.

## Deployment
My deployment target is Fly.io (using Docker to wrap up our dependencies and entrypoint)

I wanted something I didn't really have to think about too hard when deploying this, and this aligns well with my choice to try and keep everything wrapped up in a relatively small monolith with some modules to not have to deal with too many subsystems.

You can read more about this in the DEPLOYMENT.md file.
