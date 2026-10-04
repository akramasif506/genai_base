from sentence_transformers import CrossEncoder
import numpy as np


def get_re_rank(input_df,user_query,chunk_text_column):
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    input_df['re_rank_score'] = input_df[chunk_text_column].apply(lambda x : reranker.predict([[user_query,x]])[0])
    input_df['re_rank_score'] = input_df['re_rank_score'].astype(np.float64)
    reranked_df = input_df.sort_values('re_rank_score', ascending=False)
    return reranked_df
