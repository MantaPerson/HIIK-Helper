"""Utilities for reading and writing article, batch, and HIIK corpus files."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from hiik_helper.pydantic_models.article_corpus_model import ArticleCorpus, Article
from hiik_helper.pydantic_models.hiik_corpus import HiikCorpus


logger = logging.getLogger(__name__)


def _load_tool_arguments(message: dict[str, Any]) -> dict[str, Any]:
    """Return parsed function-call arguments from an OpenAI batch message."""

    arguments = message["tool_calls"][0]["function"]["arguments"]
    if isinstance(arguments, str):
        return json.loads(arguments)
    return arguments


def read_jsonl_to_article_corpus(json_path: str) -> ArticleCorpus:
    """
    Read the JSON file containing the articles and return the ArticleCorpus object containing the articles.
    The headline, subheadline, and paragraphs are required for each article in the JSON file.
    """
    all_articles: ArticleCorpus = ArticleCorpus(articles=[])
    with Path(json_path).open("r", encoding="utf-8") as file:
        for line in file:
            response = json.loads(line)
            message = response["response"]["body"]["choices"][0]["message"]
            arguments = _load_tool_arguments(message)
            articles = ArticleCorpus(**arguments)
            all_articles.articles.extend(articles.articles)

    return all_articles


def read_batch_request_jsonl_to_article_dict(json_path: str) -> dict[str, Article]:
    """
    Extracts the articles from the batch request that is sent to the GPT model.
    It returns a dictionary of ArticleCorpus.Articles where the key is the custom_id of the batch request.

    Args:
        json_path (str): The path to the JSONL file containing the batch request.
    """
    articles_dict: dict[str, Article] = {}
    with Path(json_path).open("r", encoding="utf-8") as file:
        for line in file:
            request = json.loads(line)
            custom_id = request["custom_id"]
            article = request["body"]["messages"][1]["content"]
            article_lines = article.split("\n")
            if len(article_lines) < 3:
                raise ValueError(
                    f"Batch request {custom_id} does not contain headline, subheadline, and paragraphs."
                )
            headline = article_lines[0]
            subheadline = article_lines[1]
            paragraphs = "\n".join(article_lines[2:])
            article = Article(
                Headline=headline, Subheadline=subheadline, Paragraphs=paragraphs
            )
            articles_dict[custom_id] = article

    return articles_dict


def read_batch_output_jsonl_to_hiik_corpus(
    json_path: str, article_dict: dict[str, Article]
) -> HiikCorpus:
    """
    Read the JSON file containing the article extractions and return the HiikCorpus object containing the articles.
    """
    hiik_article_corpus: HiikCorpus = HiikCorpus(articles=[])
    num_articles_parsed = 0
    num_unparseable_articles = 0
    with Path(json_path).open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                response = json.loads(line)
                custom_id = response["custom_id"]
                article = article_dict[custom_id]
                message = response["response"]["body"]["choices"][0]["message"]
                parameters = _load_tool_arguments(message)
                parameters = HiikCorpus.HiikArticle.HiikParameters(**parameters)
                hiik_article = HiikCorpus.HiikArticle(
                    article_content=article,
                    date_published=None,
                    date_accessed=None,
                    date_updated=None,
                    url=None,
                    parameters=parameters,
                )
                hiik_article_corpus.articles.append(hiik_article)
                num_articles_parsed += 1
            except (
                KeyError,
                TypeError,
                json.JSONDecodeError,
                ValidationError,
                ValueError,
            ) as exc:
                num_unparseable_articles += 1
                logger.warning(
                    "Could not parse %s line %s: %s", json_path, line_number, exc
                )

    print(f"Number of articles parsed: {num_articles_parsed}")
    print(f"Number of unparseable articles: {num_unparseable_articles}")
    return hiik_article_corpus


def save_hiik_corpus_to_jsonl(hiik_corpus: HiikCorpus, jsonl_path: str):
    """
    Save the HiikCorpus object to a JSONL file.
    """
    num_articles_saved = 0
    with Path(jsonl_path).open("a", encoding="utf-8") as file:
        for article in hiik_corpus.articles:
            article_json = article.model_dump_json()
            file.write(article_json + "\n")
            num_articles_saved += 1
    print(f"Number of articles saved: {num_articles_saved}")


def read_hiik_corpus_jsonl_to_hiik_corpus(jsonl_path: str) -> HiikCorpus:
    """
    Read the JSONL file containing the HiikCorpus and return the HiikCorpus object containing the articles.
    """
    hiik_article_corpus: HiikCorpus = HiikCorpus(articles=[])
    with Path(jsonl_path).open("r", encoding="utf-8") as file:
        for line in file:
            article = json.loads(line)
            article = HiikCorpus.HiikArticle(**article)
            hiik_article_corpus.articles.append(article)

    return hiik_article_corpus
