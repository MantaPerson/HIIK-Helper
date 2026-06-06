# HIIK Helper

HIIK Helper is a Python project for collecting conflict-related news articles and converting them into structured HIIK-style event data. It combines a Scrapy crawler with OpenAI/instructor batch workflows and Pydantic models.

## Repository Layout

- `hiik_helper/main.py` starts the Scrapy crawler.
- `hiik_helper/spiders/hiik_default_spider.py` crawls Karen News article pages and stores discovered article content.
- `hiik_helper/spiders/hiik_xml_spider.py` is a placeholder XML feed spider.
- `hiik_helper/article_generator.py` generates synthetic articles from existing examples.
- `hiik_helper/article_extractor_openai.py` creates OpenAI batch requests for extracting HIIK parameters from articles.
- `hiik_helper/utils.py` reads and writes batch JSONL output and `HiikCorpus` records.
- `hiik_helper/pydantic_models/` contains the article and HIIK corpus schemas.
- `found_articles.json` and `visited_urls.json` are crawler state/data files used by the spider.

## Requirements

- Python 3.11, as declared in `pyproject.toml`
- Poetry
- Scrapy
- OpenAI API access for generation and extraction workflows

Install dependencies:

```sh
poetry install
```

For OpenAI-backed workflows, set:

```sh
export OPENAI_API_KEY="your-api-key"
```

## Crawling Articles

The default crawler starts from `https://karennews.org/` and follows article links matching the configured article URL patterns.

```sh
poetry run python hiik_helper/main.py
```

The crawler reads `visited_urls.json` before running and writes updates to:

- `found_articles.json`
- `visited_urls.json`

The helper script `run-article-extractor.sh` runs the same crawler through a local absolute Python path. Update that path before using it on another machine.

## Generating Articles

`ArticleGenerator` samples articles from `found_articles.json`, builds few-shot prompts, and writes generated article records.

Entrypoint:

```sh
poetry run python hiik_helper/article_generator_script.py
```

Most actions in the script are currently commented out. Enable the specific generation or batch-read section you want to run.

Typical generated files include:

- `generated_articles.json`
- `batch_file.jsonl`
- `data/created_articles/batch_data/*.jsonl`

## Extracting HIIK Parameters

`ArticleExtractor` converts article text into OpenAI batch messages and expects responses matching `HiikCorpus.HiikArticle.HiikParameters`.

Entrypoint:

```sh
poetry run python hiik_helper/article_extractor_openai_script.py
```

The extraction script is also mostly configured through commented sections. The normal flow is:

1. Read generated articles into an `ArticleCorpus`.
2. Convert them into `HiikCorpus` article shells.
3. Create a batch JSONL request file.
4. Parse the OpenAI batch output JSONL.
5. Append structured records to a HIIK corpus JSONL file.

## Data Artifacts

Generated data can become large quickly and is ignored by Git:

- `data/`
- `batch_file.jsonl`
- `generated_articles.json`
- `found_articles.json`
- `visited_urls.json`

Some of these files may already be tracked in the repository history. Adding them to `.gitignore` prevents new untracked copies from appearing, but it does not stop Git from tracking files that are already in the index. Use `git rm --cached <path>` only when you intentionally want to stop tracking an existing file without deleting the local copy.

## Current Caveats

- `README.md` documents the intended workflow, but several scripts are still exploratory and use commented blocks for selecting actions.
- Some imports assume scripts are run from specific working directories rather than as installed package modules.
- The XML spider is not production-ready.
- There are no active tests beyond an empty `tests` package.
