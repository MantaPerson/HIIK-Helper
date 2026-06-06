"""Script helpers for generating synthetic articles or parsing batch output."""

from hiik_helper.article_generator import ArticleGenerator


def run_article_generator():
    """Configure and run the selected article-generation workflow."""

    # Name of the GPT model to use
    model_name = "gpt-4o-mini"

    # Temperature parameter for the GPT model
    temperature = 0.0

    # Path to the JSON file containing the articles
    article_json_path = "found_articles.json"

    # Path to the JSON file where the generated articles should be saved
    article_output_path = "generated_articles.json"

    # Number of articles to choose from the JSON file (amount used for few shot prompting)
    num_articles_to_choose = 3

    # Initialize the ArticleGenerator class
    return ArticleGenerator(
        article_json_path=article_json_path,
        article_output_path=article_output_path,
        num_articles_to_choose=num_articles_to_choose,
        model_name=model_name,
        temperature=temperature,
    )


if __name__ == "__main__":
    run_article_generator()
