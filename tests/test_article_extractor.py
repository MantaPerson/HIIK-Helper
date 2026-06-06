import sys
import types

import pytest

from hiik_helper.article_extractor_openai import ArticleExtractor
from hiik_helper.pydantic_models.article_corpus_model import Article
from hiik_helper.pydantic_models.hiik_corpus import HiikCorpus


def test_article_extractor_requires_openai_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        ArticleExtractor()


def test_article_extractor_create_message_generator_uses_article_text():
    extractor = object.__new__(ArticleExtractor)
    extractor.system_prompt = "Extract"
    corpus = HiikCorpus(
        articles=[
            HiikCorpus.HiikArticle(
                article_content=Article(
                    Headline="Headline",
                    Subheadline="Sub",
                    Paragraphs="Paragraphs",
                )
            )
        ]
    )

    messages = list(extractor.create_message_generator(corpus))

    assert messages == [
        [
            {"role": "system", "content": "Extract"},
            {"role": "user", "content": "Headline\nSub\nParagraphs"},
        ]
    ]


def test_article_extractor_create_batch_json_delegates_to_instructor(monkeypatch):
    captured = {}

    class FakeBatchJob:
        @staticmethod
        def create_from_messages(*args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs

    instructor_module = types.ModuleType("instructor")
    batch_module = types.ModuleType("instructor.batch")
    batch_module.BatchJob = FakeBatchJob
    monkeypatch.setitem(sys.modules, "instructor", instructor_module)
    monkeypatch.setitem(sys.modules, "instructor.batch", batch_module)
    extractor = object.__new__(ArticleExtractor)
    extractor.model_name = "model"
    messages = iter([[{"role": "user", "content": "Prompt"}]])

    extractor.create_batch_json(messages, "batch.jsonl")

    assert captured["args"] == (messages,)
    assert captured["kwargs"]["model"] == "model"
    assert captured["kwargs"]["response_model"] is HiikCorpus.HiikArticle.HiikParameters
    assert captured["kwargs"]["file_path"] == "batch.jsonl"
