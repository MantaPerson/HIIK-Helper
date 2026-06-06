import json

import pytest

from hiik_helper.pydantic_models.article_corpus_model import Article
from hiik_helper.pydantic_models.hiik_corpus import HiikCorpus
from hiik_helper.utils import (
    read_batch_output_jsonl_to_hiik_corpus,
    read_batch_request_jsonl_to_article_dict,
    read_hiik_corpus_jsonl_to_hiik_corpus,
    read_jsonl_to_article_corpus,
    save_hiik_corpus_to_jsonl,
)


def _batch_response(custom_id, arguments):
    return {
        "custom_id": custom_id,
        "response": {
            "body": {
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "function": {
                                        "arguments": json.dumps(arguments),
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
    }


def _hiik_parameters():
    return {
        "date_of_events": "2024-08-01",
        "type_of_events": {
            "event_type": "Shelling",
            "event_type_mod": "(conflicting)",
        },
        "actor_a": {
            "actor_name": "Actor A",
            "affiliation": "government",
            "additional_attributes": None,
        },
        "actor_b": {
            "actor_name": "Actor B",
            "affiliation": "civilian",
            "additional_attributes": None,
        },
        "issue": "Issue",
        "description": "Description",
        "country": "Myanmar",
        "region": None,
        "city": None,
        "weapon": None,
        "personnel": "Under 50",
        "fatalities": [],
        "injured": [],
        "refugees": [],
        "destruction": [],
        "comments": "None",
    }


def test_read_jsonl_to_article_corpus_parses_tool_arguments(tmp_path):
    path = tmp_path / "batch_output.jsonl"
    path.write_text(
        json.dumps(
            _batch_response(
                "request-1",
                {
                    "articles": [
                        {
                            "Headline": "Headline",
                            "Subheadline": "Sub",
                            "Paragraphs": "Body",
                        }
                    ]
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )

    corpus = read_jsonl_to_article_corpus(str(path))

    assert len(corpus.articles) == 1
    assert corpus.articles[0].Subheadline == "Sub"


def test_read_jsonl_to_article_corpus_accepts_dict_tool_arguments(tmp_path):
    path = tmp_path / "batch_output.jsonl"
    response = _batch_response(
        "request-1",
        {
            "articles": [
                {
                    "Headline": "Headline",
                    "Subheadline": "Sub",
                    "Paragraphs": "Body",
                }
            ]
        },
    )
    response["response"]["body"]["choices"][0]["message"]["tool_calls"][0]["function"][
        "arguments"
    ] = {
        "articles": [
            {
                "Headline": "Dict headline",
                "Subheadline": "Sub",
                "Paragraphs": "Body",
            }
        ]
    }
    path.write_text(json.dumps(response) + "\n", encoding="utf-8")

    corpus = read_jsonl_to_article_corpus(str(path))

    assert corpus.articles[0].Headline == "Dict headline"


def test_read_batch_request_jsonl_to_article_dict(tmp_path):
    path = tmp_path / "request.jsonl"
    path.write_text(
        json.dumps(
            {
                "custom_id": "request-1",
                "body": {
                    "messages": [
                        {"role": "system", "content": "Extract"},
                        {"role": "user", "content": "Headline\nSub\nBody"},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    articles = read_batch_request_jsonl_to_article_dict(str(path))

    assert articles["request-1"].Headline == "Headline"
    assert articles["request-1"].Paragraphs == "Body"


def test_read_batch_request_jsonl_to_article_dict_rejects_short_prompt(tmp_path):
    path = tmp_path / "request.jsonl"
    path.write_text(
        json.dumps(
            {
                "custom_id": "request-1",
                "body": {
                    "messages": [
                        {"role": "system", "content": "Extract"},
                        {"role": "user", "content": "Headline\nSub"},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="headline, subheadline, and paragraphs"):
        read_batch_request_jsonl_to_article_dict(str(path))


def test_read_batch_output_jsonl_to_hiik_corpus_skips_malformed_rows(tmp_path):
    path = tmp_path / "output.jsonl"
    path.write_text(
        json.dumps(_batch_response("request-1", _hiik_parameters()))
        + "\n"
        + json.dumps({"custom_id": "bad-row"})
        + "\n",
        encoding="utf-8",
    )
    article_dict = {
        "request-1": Article(
            Headline="Headline",
            Subheadline="Sub",
            Paragraphs="Body",
        )
    }

    corpus = read_batch_output_jsonl_to_hiik_corpus(str(path), article_dict)

    assert len(corpus.articles) == 1
    assert corpus.articles[0].parameters.actor_a.actor_name == "Actor A"


def test_read_batch_output_jsonl_to_hiik_corpus_logs_malformed_rows(tmp_path, caplog):
    path = tmp_path / "output.jsonl"
    path.write_text(json.dumps({"custom_id": "bad-row"}) + "\n", encoding="utf-8")

    corpus = read_batch_output_jsonl_to_hiik_corpus(str(path), {})

    assert corpus.articles == []
    assert "Could not parse" in caplog.text


def test_hiik_corpus_jsonl_round_trip(tmp_path):
    path = tmp_path / "hiik_corpus.jsonl"
    article = HiikCorpus.HiikArticle(
        article_content=Article(
            Headline="Headline", Subheadline="Sub", Paragraphs="Body"
        ),
        parameters=HiikCorpus.HiikArticle.HiikParameters(**_hiik_parameters()),
    )

    save_hiik_corpus_to_jsonl(HiikCorpus(articles=[article]), str(path))
    loaded = read_hiik_corpus_jsonl_to_hiik_corpus(str(path))

    assert len(loaded.articles) == 1
    assert loaded.articles[0].article_content.Headline == "Headline"
    assert loaded.articles[0].parameters.type_of_events.event_type == "Shelling"
