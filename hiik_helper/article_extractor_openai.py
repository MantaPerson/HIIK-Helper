from openai import OpenAI
from instructor.batch import BatchJob
from instructor import from_openai
from pydantic_models.hiik_corpus import HiikCorpus
import os


class ArticleExtractor:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        """
        The ArticleExtractor will extract the information from the articles using the GPT model.
        The information extracted is as follows and corresponds to the HiikCorpus.HiikParameters model:
            - date_of_events: str : Date of the events (can be a time span)
            - type_of_events: str : Type of the events e.g. Airstrike, Artillery shelling, release of POWs, in parentheses it should be either said if it was (conflicting) or (resolving)
            - actor_a: str : Actor A involved in the events (can be a group, country, etc.), if the source mentions something like christian or jobless add it in parentheses, if it mentions an organization or a country, add it in square brackets
            - actor_b: str : Actor A involved in the events (can be a group, country, etc.), if the source mentions something like christian or jobless add it in parentheses, if it mentions an organization or a country, add it in square brackets
            - issue: str : Issue that was the catalyst for the events like the implementation of a controversial law, the imprisonment of a political figure, etc.
            - description: str : Description of the events, what happened, how many people were involved, when did it happen, etc. should be brief and concise but informative
            - country: str : Country where the events took place
            - region: str : Region where the events took place
            - city: str : City, town or village where the events took place
            - weapon: str : Weapon used in the events, e.g. artillery, small arms, light weapons, jets, etc.
            - personnel: PersonnelType : Personnel involved in the events, can be Under 50, 50-400, Over 400
            - fatalities: PeopleInvolved : Number of fatalities and the group of people involved
            - injured: PeopleInvolved : Number of injured people and the group of people involved
            - refugees: PeopleInvolved : Number of refugees/IDP and the group of people involved
            - destruction: str : Level of destruction caused by the events, e.g. medium damage to infrastructure, 1 mosque destroyed, 2 houses burned, 2 cars damaged etc.
            - comments: str : Any additional comments or notes about the events

        These parameters are then combined with the article itself into a HiikCorpus object.
        This can then be used to train models.

        Args:
            model_name (str): The name of the GPT model to use.
            temperature (float): The temperature parameter for the GPT model.
        """
        self.model_name = model_name
        self.temperature = temperature
        if os.getenv("OPENAI_API_KEY") is not None:
            self.client = from_openai(OpenAI())
        else:
            print(
                "No OpenAI API key found. Please set the OPENAI_API_KEY environment variable."
            )

        self.system_prompt: str = "Extract the parameters from the article:"

    def create_message_generator(self, hiik_article_corpus: HiikCorpus):
        """
        Returns a generator that will generate the messages to be used with instructors BatchJob.
        BatchJob will then send the messages to the GPT model to extract the parameters (using BatchAPI).
        """

        for article in hiik_article_corpus.articles:
            prompt = (
                article.article_content.Headline
                + "\n"
                + article.article_content.Subheadline
                + "\n"
                + article.article_content.Paragraphs
            )
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            yield messages

    def create_batch_json(self, message_generator, batch_jsonl_path: str):
        """
        Creates a JSONL file containing the messages to be used with instructors BatchJob.
        BatchJob will then send the messages to the GPT model to extract the parameters (using BatchAPI).
        """

        BatchJob.create_from_messages(
            message_generator,
            model=self.model_name,
            response_model=HiikCorpus.HiikArticle.HiikParameters,
            file_path=batch_jsonl_path,
        )
