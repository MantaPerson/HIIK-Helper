"""Script helpers for preparing and parsing OpenAI HIIK extraction batches."""

from article_extractor_openai import ArticleExtractor
from pydantic_models.hiik_corpus import (
    HiikCorpus,
    read_article_corpus_into_hiik_articles,
)
from pydantic_models.article_corpus_model import read_json_to_article_corpus
from utils import (
    read_batch_output_jsonl_to_hiik_corpus,
    read_batch_request_jsonl_to_article_dict,
    save_hiik_corpus_to_jsonl,
    read_hiik_corpus_jsonl_to_hiik_corpus,
)

input_article_batch_file_path = "generated_articles.json"
index = "C"
output_batch_jsonl_path = (
    f"data/extracted_articles/batch_data/parameter_extraction_batch_{index}.jsonl"
)
parameter_extracted_batch_path = (
    f"data/extracted_articles/batch_data/extraction_{index}.jsonl"
)
saved_hiik_corpus_path = (
    "data/extracted_articles/hiik_corpus/hiik_corpus_complete.jsonl"
)

# article_corpus = read_json_to_article_corpus(input_article_batch_file_path)
# hiik_article_corpus = read_article_corpus_into_hiik_articles(
#     article_corpus=article_corpus
# )
# article_extractor = ArticleExtractor(model_name="gpt-4o-mini", temperature=0.0)
# limited_hiik_article_corpus = HiikCorpus(
#     articles=hiik_article_corpus.articles[7_000:12_000]
# )
# message_generator = article_extractor.create_message_generator(
#     hiik_article_corpus=limited_hiik_article_corpus
# )
# article_extractor.create_batch_json(
#     message_generator, batch_jsonl_path=output_batch_jsonl_path
# )


# article_dict = read_batch_request_jsonl_to_article_dict(
#     json_path=output_batch_jsonl_path
# )
# hiik_corpus: HiikCorpus = read_batch_output_jsonl_to_hiik_corpus(
#     json_path=parameter_extracted_batch_path, article_dict=article_dict
# )
# save_hiik_corpus_to_jsonl(hiik_corpus=hiik_corpus, jsonl_path=saved_hiik_corpus_path)

read_hiik_corpus = read_hiik_corpus_jsonl_to_hiik_corpus(
    jsonl_path=saved_hiik_corpus_path
)


print()
