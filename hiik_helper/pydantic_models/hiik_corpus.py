"""Pydantic models for HIIK-style article and conflict-event parameters."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from hiik_helper.pydantic_models.article_corpus_model import ArticleCorpus, Article


class HiikCorpus(BaseModel):
    """
    Store HIIK articles and their extracted conflict-event parameters.
    """

    class HiikArticle(BaseModel):
        """
        This class is used to store the HIIK article and its respective parameters.
        """

        class HiikParameters(BaseModel):
            """
            The extracted parameters of the HIIK article.
            """

            class PersonnelType(Enum):
                UNDER_50 = "Under 50"
                FROM_50_TO_400 = "50-400"
                OVER_400 = "Over 400"

            class Actor(BaseModel):
                actor_name: str = Field(
                    description="Name of the actor involved in the events, e.g. ISIS subgroup, Myanmar military, etc."
                )
                affiliation: Optional[str] = Field(
                    default=None,
                    description="Affiliation of the actor, e.g. government, rebel group, ISIS, etc.",
                )
                additional_attributes: Optional[str] = Field(
                    default=None,
                    description="Additional attributes of the actor, e.g. Christian, jobless, etc.",
                )

            class PeopleInvolved(BaseModel):
                count: int = Field(
                    description="Number of people of a particular group involved"
                )
                group: str = Field(
                    description="Group of people involved, can be civilians, faction members, etc."
                )
                at_least: bool = Field(
                    description="Whether the count is at least the given number (only if the count is an estimate)"
                )

            class TypeOfEvent(BaseModel):
                class EventType(Enum):
                    CONFLICTING = "(conflicting)"
                    RESOLVING = "(resolving)"
                    NEUTRAL = "(neutral)"

                event_type: str = Field(
                    description="Type of the events e.g. Airstrike, Artillery shelling, release of POWs"
                )
                event_type_mod: EventType = Field(
                    description="Whether the event is conflicting or resolving"
                )

            class ObjectDestroyed(BaseModel):
                object: str = Field(description="Object destroyed")
                count: int = Field(description="Number of objects destroyed")
                level_of_destruction: str = Field(description="Level of destruction")

            class WeaponsUsed(BaseModel):
                weapons: list[str] = Field(
                    description=(
                        "List of weapon classes and specific weapons, e.g. "
                        "Heavy Weapons (Jets; Helicopters) or Light Weapons."
                    )
                )

            date_of_events: str = Field(
                description="Date of the events (as specific as possible)"
            )
            type_of_events: TypeOfEvent = Field(description="Type of the events.")
            actor_a: Actor = Field(description="Actor A involved in the events.")
            actor_b: Actor = Field(description="Actor A involved in the events.")
            issue: str = Field(
                description=(
                    "Issue that catalyzed the events, such as a controversial "
                    "law or the imprisonment of a political figure."
                )
            )
            description: str = Field(
                description=(
                    "Brief description of what happened, when it happened, "
                    "and how many people were involved."
                )
            )
            country: str = Field(
                description="Country or countries where the events took place"
            )
            region: Optional[str] = Field(
                description="Region or state inside the countries where the events took place"
            )
            city: Optional[str] = Field(
                description="City, town or village where the events took place."
            )
            weapon: Optional[WeaponsUsed] = Field(
                description="List of the weapons used in the events."
            )
            personnel: PersonnelType = Field(
                description=(
                    "Personnel actively involved in the events, excluding "
                    "refugees and victims."
                )
            )
            fatalities: list[PeopleInvolved] = Field(
                description="Number of fatalities and the group of people involved"
            )
            injured: list[PeopleInvolved] = Field(
                description="Number of injured people and the group of people involved"
            )
            refugees: list[PeopleInvolved] = Field(
                description="Number of refugees/IDP and the group of people involved"
            )
            destruction: list[ObjectDestroyed] = Field(
                description=(
                    "Objects destroyed or harmed during the events. Only "
                    "actual damage counts."
                )
            )
            comments: str = Field(
                description="Any additional comments or notes about the events"
            )

        article_content: Optional[Article] = Field(default=None, description="Article")
        date_published: Optional[str] = Field(
            default=None, description="Publication date of the article"
        )
        date_accessed: Optional[str] = Field(
            default=None, description="Date the article was accessed"
        )
        date_updated: Optional[str] = Field(
            default=None, description="Date the article was last updated"
        )
        url: Optional[str] = Field(default=None, description="URL of the article")
        parameters: Optional[HiikParameters] = Field(
            default=None, description="Parameters of the article"
        )

    articles: list[HiikArticle]


def read_article_corpus_into_hiik_articles(article_corpus: ArticleCorpus):
    """Wrap plain article records in empty HIIK article shells."""

    hiik_article_corpus = HiikCorpus(articles=[])
    for article_corpus_article in article_corpus.articles:
        hiik_article = HiikCorpus.HiikArticle(
            article_content=article_corpus_article,
            date_published=None,
            date_accessed=None,
            date_updated=None,
            url=None,
            parameters=None,
        )
        hiik_article_corpus.articles.append(hiik_article)
    return hiik_article_corpus
