from vertexai.language_models import TextEmbeddingModel

def get_text_embedding(input_text):
    embed_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    text_embedding = embed_model.get_embeddings([input_text])[0].values
    return text_embedding
