import json

import pytest
from pydantic import ValidationError

from hiik_helper.pydantic_models.article_corpus_model import (
    Article,
    ArticleCorpus,
    read_json_to_article_corpus,
)


def test_article_is_exported_model():
    article = Article(Headline="Headline", Subheadline="Sub", Paragraphs="Body")
    nested_alias_article = ArticleCorpus.Article(
        Headline="Nested",
        Subheadline="Alias",
        Paragraphs="Body",
    )

    corpus = ArticleCorpus(articles=[article])

    assert corpus.articles[0].Headline == "Headline"
    assert nested_alias_article.Headline == "Nested"


def test_read_json_to_article_corpus_supports_list_files(tmp_path):
    path = tmp_path / "generated_articles.json"
    path.write_text(
        json.dumps(
            [
                {
                    "headline": "Headline",
                    "subheadline": "Sub",
                    "paragraphs": "Body",
                }
            ]
        ),
        encoding="utf-8",
    )

    corpus = read_json_to_article_corpus(str(path))

    assert len(corpus.articles) == 1
    assert corpus.articles[0].Paragraphs == "Body"


def test_read_json_to_article_corpus_supports_url_keyed_files(tmp_path):
    path = tmp_path / "found_articles.json"
    path.write_text(
        json.dumps(
            {
                "https://example.test/article": {
                    "headline": "Headline",
                    "subheadline": "Sub",
                    "paragraphs": "Body",
                }
            }
        ),
        encoding="utf-8",
    )

    corpus = read_json_to_article_corpus(str(path))

    assert len(corpus.articles) == 1
    assert corpus.articles[0].Headline == "Headline"


def test_article_requires_all_text_fields():
    with pytest.raises(ValidationError):
        Article(Headline="Headline", Subheadline="Sub")


def test_read_json_to_article_corpus_rejects_unsupported_shape(tmp_path):
    path = tmp_path / "bad_articles.json"
    path.write_text(json.dumps({"headline": "Missing wrapper"}), encoding="utf-8")

    with pytest.raises(TypeError):
        read_json_to_article_corpus(str(path))
