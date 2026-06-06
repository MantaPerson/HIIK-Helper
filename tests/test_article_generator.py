import json
import sys
import types

import pytest

from hiik_helper.article_generator import ArticleGenerator
from hiik_helper.pydantic_models.article_corpus_model import Article, ArticleCorpus


def test_create_openai_prompt_does_not_mutate_articles():
    generator = object.__new__(ArticleGenerator)
    articles = [
        {
            "headline": "Headline",
            "subheadline": "Sub",
            "paragraphs": "Body\nLorem ipsum dolor sit amet, consectetur.",
        }
    ]

    prompt = generator.create_openai_prompt(articles)

    assert "Lorem ipsum" not in prompt
    assert "Lorem ipsum" in articles[0]["paragraphs"]


def test_article_generator_requires_openai_api_key(tmp_path, monkeypatch):
    article_path = tmp_path / "found_articles.json"
    article_path.write_text(json.dumps({}), encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        ArticleGenerator(article_json_path=str(article_path))


def test_choose_random_articles_uses_configured_sample_size(monkeypatch):
    generator = object.__new__(ArticleGenerator)
    generator.num_articles_to_choose = 2
    generator.articles = {
        "a": {"headline": "A"},
        "b": {"headline": "B"},
        "c": {"headline": "C"},
    }

    monkeypatch.setattr(
        "hiik_helper.article_generator.random.sample", lambda keys, n: ["c", "a"]
    )

    assert generator.choose_random_articles() == [
        {"headline": "C"},
        {"headline": "A"},
    ]


def test_save_generated_articles_creates_and_appends_output(tmp_path):
    output_path = tmp_path / "generated_articles.json"
    generator = object.__new__(ArticleGenerator)
    generator.article_output_path = str(output_path)
    articles = ArticleCorpus(
        articles=[
            Article(Headline="First", Subheadline="Sub", Paragraphs="Body"),
            Article(Headline="Second", Subheadline="Sub", Paragraphs="Body"),
        ]
    )

    generator.save_generated_articles(articles)
    generator.save_generated_articles(
        ArticleCorpus(
            articles=[
                Article(Headline="Third", Subheadline="Sub", Paragraphs="Body"),
            ]
        )
    )

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert [article["headline"] for article in saved] == ["First", "Second", "Third"]


def test_create_message_generator_uses_sampled_articles():
    generator = object.__new__(ArticleGenerator)
    generator.system_prompt = "Generate"
    generator.choose_random_articles = lambda: [
        {
            "headline": "Headline",
            "subheadline": "Sub",
            "paragraphs": "Body",
        }
    ]

    messages = list(generator.create_message_generator(2))

    assert len(messages) == 2
    assert messages[0][0] == {"role": "system", "content": "Generate"}
    assert (
        messages[0][1]["content"]
        == "Headline: Headline\nSubheadline: Sub\nParagraphs: Body\n"
    )


def test_send_openai_request_passes_model_prompt_and_response_model():
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return "response"

    class FakeClient:
        class Chat:
            completions = FakeCompletions()

        chat = Chat()

    generator = object.__new__(ArticleGenerator)
    generator.client = FakeClient()
    generator.model_name = "model"
    generator.temperature = 0.25
    generator.system_prompt = "System"

    response = generator.send_openai_request("Prompt")

    assert response == "response"
    assert captured["model"] == "model"
    assert captured["temperature"] == 0.25
    assert captured["response_model"] is ArticleCorpus
    assert captured["messages"] == [
        {"role": "system", "content": "System"},
        {"role": "user", "content": "Prompt"},
    ]


def test_generate_once_samples_sends_and_saves():
    calls = []
    generator = object.__new__(ArticleGenerator)
    generator.choose_random_articles = lambda: calls.append("choose") or [
        {"headline": "H"}
    ]
    generator.create_openai_prompt = (
        lambda articles: calls.append(("prompt", articles)) or "prompt"
    )
    generator.send_openai_request = (
        lambda prompt: calls.append(("send", prompt)) or "response"
    )
    generator.save_generated_articles = lambda response: calls.append(
        ("save", response)
    )

    generator.generate_once()

    assert calls == [
        "choose",
        ("prompt", [{"headline": "H"}]),
        ("send", "prompt"),
        ("save", "response"),
    ]


def test_create_batch_json_delegates_to_instructor(monkeypatch):
    captured = {}

    class FakeBatchJob:
        @staticmethod
        def create_from_messages(**kwargs):
            captured.update(kwargs)

    instructor_module = types.ModuleType("instructor")
    batch_module = types.ModuleType("instructor.batch")
    batch_module.BatchJob = FakeBatchJob
    monkeypatch.setitem(sys.modules, "instructor", instructor_module)
    monkeypatch.setitem(sys.modules, "instructor.batch", batch_module)
    generator = object.__new__(ArticleGenerator)
    generator.model_name = "model"
    messages = iter([[{"role": "user", "content": "Prompt"}]])

    generator.create_batch_json(messages, "batch.jsonl")

    assert captured == {
        "messages_batch": messages,
        "model": "model",
        "file_path": "batch.jsonl",
        "response_model": ArticleCorpus,
    }


def test_read_batch_response_jsonl_saves_each_parsed_article(monkeypatch):
    saved = []

    class FakeBatchJob:
        @staticmethod
        def parse_from_file(file_path, response_model):
            assert file_path == "response.jsonl"
            assert response_model is ArticleCorpus
            return ["article-1", "article-2"], ["bad-row"]

    instructor_module = types.ModuleType("instructor")
    batch_module = types.ModuleType("instructor.batch")
    batch_module.BatchJob = FakeBatchJob
    monkeypatch.setitem(sys.modules, "instructor", instructor_module)
    monkeypatch.setitem(sys.modules, "instructor.batch", batch_module)
    generator = object.__new__(ArticleGenerator)
    generator.save_generated_articles = saved.append

    generator.read_batch_response_jsonl("response.jsonl")

    assert saved == ["article-1", "article-2"]
