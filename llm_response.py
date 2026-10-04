from vertexai.generative_models import GenerativeModel
import json

gen_model = GenerativeModel("gemini-2.5-flash")

def get_llm_response(input_content):
    prompt = "Anwser based on the below context \n " + str(input_content)
    response = gen_model.generate_content(prompt)
    llm_response_text = response.text
    llm_meta_data = response.usage_metadata
    prompt_token_count = llm_meta_data.prompt_token_count
    candidates_token_count = llm_meta_data.candidates_token_count
    total_token_count = llm_meta_data.total_token_count
    thoughts_token_count = llm_meta_data.thoughts_token_count
    return llm_response_text,prompt_token_count,candidates_token_count,total_token_count,thoughts_token_count
