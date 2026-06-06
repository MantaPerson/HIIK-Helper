from pydantic_models.article_corpus_model import ArticleCorpus, Article
from pydantic_models.hiik_corpus import HiikCorpus
from pydantic import ValidationError
import json
from instructor.batch import BatchJob
import os


def read_jsonl_to_article_corpus(json_path: str) -> ArticleCorpus:
    """
    Read the JSON file containing the articles and return the ArticleCorpus object containing the articles.
    The headline, subheadline, and paragraphs are required for each article in the JSON file.
    """
    all_articles: ArticleCorpus = ArticleCorpus(articles=[])
    with open(json_path, "r") as file:
        for line in file:
            articles = json.loads(line)
            articles = articles["response"]["body"]["choices"][0]["message"][
                "tool_calls"
            ][0]["function"]["arguments"]["articles"]
            articles = ArticleCorpus(articles=articles)
            for article in articles:
                article_obj = ArticleCorpus.Article(
                    Headline=article["headline"],
                    Subheadline=article["subheadline"],
                    Paragraphs=article["paragraphs"],
                )
                all_articles.articles.append(article_obj)

    return all_articles


def read_batch_request_jsonl_to_article_dict(json_path: str) -> dict[str, Article]:
    """
    Extracts the articles from the batch request that is sent to the GPT model.
    It returns a dictionary of ArticleCorpus.Articles where the key is the custom_id of the batch request.

    Args:
        json_path (str): The path to the JSONL file containing the batch request.
    """
    articles_dict: dict[str, Article] = {}
    with open(json_path, "r") as file:
        for line in file:
            request = json.loads(line)
            custom_id = request["custom_id"]
            article = request["body"]["messages"][1]["content"]
            article_lines = article.split("\n")
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
    with open(json_path, "r") as file:
        for line in file:
            try:
                response = json.loads(line)
                custom_id = response["custom_id"]
                article = article_dict[custom_id]
                parameters = json.loads(
                    response["response"]["body"]["choices"][0]["message"]["tool_calls"][
                        0
                    ]["function"]["arguments"]
                )
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
            except:
                num_unparseable_articles += 1

    print(f"Number of articles parsed: {num_articles_parsed}")
    print(f"Number of unparseable articles: {num_unparseable_articles}")
    return hiik_article_corpus


def save_hiik_corpus_to_jsonl(hiik_corpus: HiikCorpus, jsonl_path: str):
    """
    Save the HiikCorpus object to a JSONL file.
    """
    num_articles_saved = 0
    with open(jsonl_path, "a") as file:
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
    with open(jsonl_path, "r") as file:
        for line in file:
            article = json.loads(line)
            article = HiikCorpus.HiikArticle(**article)
            hiik_article_corpus.articles.append(article)

    return hiik_article_corpus
