import pytest
from pydantic import ValidationError

from hiik_helper.pydantic_models.article_corpus_model import Article, ArticleCorpus
from hiik_helper.pydantic_models.hiik_corpus import (
    HiikCorpus,
    read_article_corpus_into_hiik_articles,
)


def test_hiik_actor_optional_fields_default_to_none():
    actor = HiikCorpus.HiikArticle.HiikParameters.Actor(actor_name="Actor")

    assert actor.affiliation is None
    assert actor.additional_attributes is None


def test_hiik_parameters_reject_invalid_event_modifier():
    with pytest.raises(ValidationError):
        HiikCorpus.HiikArticle.HiikParameters.TypeOfEvent(
            event_type="Shelling",
            event_type_mod="invalid",
        )


def test_read_article_corpus_into_hiik_articles_preserves_article_content():
    article = Article(Headline="Headline", Subheadline="Sub", Paragraphs="Body")

    hiik_corpus = read_article_corpus_into_hiik_articles(
        ArticleCorpus(articles=[article])
    )

    assert len(hiik_corpus.articles) == 1
    assert hiik_corpus.articles[0].article_content == article
    assert hiik_corpus.articles[0].parameters is None
