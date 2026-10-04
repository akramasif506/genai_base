import json

config_dict = {
	"bq_table_name" : "movies_db.movies_extended_embedded",
	"embedding_col" : "embedding",
	"chunk_text_column" : "chunk_text",
    "retrieve_cols" : ['chunk_text','similarity_score'],
    "re_rank_cols" : ['chunk_text','similarity_score','re_rank_score']
    }

def get_config():
    return config_dict
