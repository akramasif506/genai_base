import numpy as np

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_candidates(inut_df,embedding_col,query_embedding, top_k=3):
    #query_embedding = embed_model.get_embeddings([query])[0].values
    inut_df['similarity_score'] = inut_df[embedding_col].apply(
        lambda x: cosine_similarity(query_embedding, x)
    )
    retrieved_df = inut_df.sort_values('similarity_score', ascending=False).head(top_k)
    return retrieved_df
