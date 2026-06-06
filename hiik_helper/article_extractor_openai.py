"""OpenAI batch request builder for extracting HIIK parameters from articles."""

import os

from hiik_helper.pydantic_models.hiik_corpus import HiikCorpus


class ArticleExtractor:
    """Create structured extraction requests for a corpus of HIIK articles."""

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        """Initialize the OpenAI-backed HIIK parameter extractor.

        The model response is validated against
        ``HiikCorpus.HiikArticle.HiikParameters`` and can then be combined with
        article text into a structured training corpus.

        Args:
            model_name (str): The name of the GPT model to use.
            temperature (float): The temperature parameter for the GPT model.
        """
        self.model_name = model_name
        self.temperature = temperature
        if os.getenv("OPENAI_API_KEY") is None:
            raise RuntimeError(
                "No OpenAI API key found. Please set the OPENAI_API_KEY environment variable."
            )

        from openai import OpenAI
        from instructor import from_openai

        self.client = from_openai(OpenAI())

        self.system_prompt: str = "Extract the parameters from the article:"

    def create_message_generator(self, hiik_article_corpus: HiikCorpus):
        """Yield chat messages for Instructor's batch API extraction requests."""

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
        """Create an Instructor batch JSONL file for HIIK parameter extraction."""
        from instructor.batch import BatchJob

        BatchJob.create_from_messages(
            message_generator,
            model=self.model_name,
            response_model=HiikCorpus.HiikArticle.HiikParameters,
            file_path=batch_jsonl_path,
        )
