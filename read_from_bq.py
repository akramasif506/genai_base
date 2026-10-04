from google.cloud import bigquery


bg_client = bigquery.Client()

def get_bq_df(bq_table_name):
    sql_query = "select * from " + bq_table_name
    read_bq_df = bg_client.query(sql_query).to_dataframe()
    return read_bq_df
