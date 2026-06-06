"""Script helpers for preparing and parsing OpenAI HIIK extraction batches."""

from hiik_helper.utils import read_hiik_corpus_jsonl_to_hiik_corpus

SAVED_HIIK_CORPUS_PATH = (
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
    jsonl_path=SAVED_HIIK_CORPUS_PATH
)


print()
