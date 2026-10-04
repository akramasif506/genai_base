from fastapi import FastAPI
from fastapi import FastAPI, Header, HTTPException,Depends
import os
from pydantic import BaseModel
from read_from_bq import get_bq_df
from config_details import get_config
from text_embedding import get_text_embedding
from retrieve_top_k_similar_candidate import retrieve_candidates
from re_ranker import get_re_rank
import uuid
from gcp_cloud_logging import get_logger
from datetime import datetime
from llm_response import get_llm_response

app = FastAPI()

config_dict = get_config()

logger_name = "RAG Log"
log_level = "INFO"

logger = get_logger(logger_name,log_level)

## This is just for simple authentication purpose
API_KEY = os.environ.get("RAG_API_KEY")

class Query_base(BaseModel):
    query : str
    top_k : int

class Query_new(BaseModel):
    query : str
    top_k : int
    top_r : int

def api_response_formatter(request_id,query,llm_response_text,prompt_token_count,candidates_token_count,total_token_count,thoughts_token_count,request_completion_duration,context_str):
    output_dict = {}
    output_dict['request_id'] = request_id
    output_dict['user_query'] = query
    output_dict['llm_response_text'] = llm_response_text
    output_dict['prompt_token_count'] = prompt_token_count
    output_dict['candidates_token_count'] = candidates_token_count
    output_dict['total_token_count'] = total_token_count
    output_dict['thoughts_token_count'] = thoughts_token_count
    output_dict['request_completion_duration'] = request_completion_duration
    output_dict['rag_context_retrieved'] = context_str
    return output_dict
    

@app.post("/retrieve")
def retrieve_top_k(input_param : Query_base):
    request_id = str(uuid.uuid4())
    request_start_time = datetime.now()
    query = input_param.query
    top_k = input_param.top_k
    logger.info({"retrievel_id": request_id , "query" : query, "top_k" : top_k})
    bq_table_name = config_dict.get('bq_table_name')
    embedding_col = config_dict.get('embedding_col')
    retrieve_cols = config_dict.get('retrieve_cols')
    query_embedding = get_text_embedding(query)
    t0 = datetime.now()
    read_bq_df = get_bq_df(bq_table_name)
    t1 = datetime.now()
    logger.info({"Stage" : "ReadFromBQ" , "Duration_in_seconds" : (t1 - t0).total_seconds() , "Status" : "Completed" })
    t0 = datetime.now()
    retrieved_df = retrieve_candidates(read_bq_df,embedding_col,query_embedding, top_k=top_k)
    t1 = datetime.now()
    logger.info({"Stage" : "VectorSearch" , "Duration_in_seconds" : (t1 - t0).total_seconds() , "Status" : "Completed" })
    context_str = retrieved_df[retrieve_cols].to_json(orient="records", date_format="iso")
    t0 = datetime.now()
    llm_response_text,prompt_token_count,candidates_token_count,total_token_count,thoughts_token_count = get_llm_response(context_str)
    t1 = datetime.now()
    logger.info({"Stage" : "LLMResponse" , "Duration_in_seconds" : (t1 - t0).total_seconds() , "Status" : "Completed" })
    request_end_time = datetime.now()
    request_completion_duration = (request_end_time - request_start_time).total_seconds()
    response_payload = api_response_formatter(request_id,query,llm_response_text,prompt_token_count,candidates_token_count,total_token_count,thoughts_token_count,request_completion_duration,context_str)
    return response_payload


@app.post("/rerank")
def re_rank_top_k(input_param : Query_new):
    request_id = str(uuid.uuid4())
    request_start_time = datetime.now()
    query = input_param.query
    top_k = input_param.top_k
    top_r = input_param.top_r
    logger.info({"retrievel_id": request_id , "query" : query, "top_k" : top_k , "top_r" : top_r})
    bq_table_name = config_dict.get('bq_table_name')
    embedding_col = config_dict.get('embedding_col')
    retrieve_cols = config_dict.get('retrieve_cols')
    chunk_text_column = config_dict.get('chunk_text_column')
    re_rank_cols = config_dict.get('re_rank_cols')
    query_embedding = get_text_embedding(query)
    t0 = datetime.now()
    read_bq_df = get_bq_df(bq_table_name)
    t1 = datetime.now()
    logger.info({"Stage" : "ReadFromBQ" , "Duration_in_seconds" : (t1 - t0).total_seconds() , "Status" : "Completed" })
    t0 = datetime.now()
    retrieved_df = retrieve_candidates(read_bq_df,embedding_col,query_embedding, top_k=top_k)
    t1 = datetime.now()
    logger.info({"Stage" : "VectorSearch" , "Duration_in_seconds" : (t1 - t0).total_seconds() , "Status" : "Completed" })
    t0 = datetime.now()
    re_ranked_df = get_re_rank(retrieved_df,query,chunk_text_column)
    t1 = datetime.now()
    logger.info({"Stage" : "Re-Ranking" , "Duration_in_seconds" : (t1 - t0).total_seconds() , "Status" : "Completed" })
    context_str = re_ranked_df[re_rank_cols].to_json(orient="records", date_format="iso")
    t0 = datetime.now()
    llm_response_text,prompt_token_count,candidates_token_count,total_token_count,thoughts_token_count = get_llm_response(context_str)
    t1 = datetime.now()
    logger.info({"Stage" : "LLMResponse" , "Duration_in_seconds" : (t1 - t0).total_seconds() , "Status" : "Completed" })
    request_end_time = datetime.now()
    request_completion_duration = (request_end_time - request_start_time).total_seconds()
    response_payload = api_response_formatter(request_id,query,llm_response_text,prompt_token_count,candidates_token_count,total_token_count,thoughts_token_count,request_completion_duration,context_str)
    return response_payload

def verify_api_key(rag_api_key: str = Header(...)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail='Server misconfigured: API key not set, Pass -H "rag-api-key: YOUR_API_KEY"')
    if rag_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.post("/ask")
def test(input_param : Query_base,api_test=Depends(verify_api_key)):
    return input_param

@app.get("/health")
def health():
    return {"status": "ok"}
