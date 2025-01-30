import openai
import bert_score
from .config import GPT_API_BASE, GPT_API_KEY
from tqdm import tqdm

bert_scorer = None

# 计算向量余弦相似度
def calculate_cosine_similarity(vector1, vector2):
    # Calculate cosine similarity between two vectors
    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    magnitude1 = sum(a ** 2 for a in vector1) ** 0.5
    magnitude2 = sum(b ** 2 for b in vector2) ** 0.5
    cosine_similarity = dot_product / (magnitude1 * magnitude2)
    return cosine_similarity

# 调用GPT接口对文本对进行embedding并计算相似度
def GPT_text_Similarity(sentence1, sentence2, model_type):
    openai.api_base = GPT_API_BASE
    openai.api_key = GPT_API_KEY
    response = openai.Embedding.create(model=model_type, input=[sentence1, sentence2])
    embedding1 = response['data'][0]['embedding']
    embedding2 = response['data'][1]['embedding']
    # Calculate sentence similarity, e.g., using cosine similarity
    similarity = calculate_cosine_similarity(embedding1, embedding2)
    return similarity

# 计算BERT相似度
def BERTScore_Similarity( sentence1, sentence2, model_type ):
    global bert_scorer
    if bert_scorer == None:
        bert_scorer = bert_score.BERTScorer( model_type=model_type, lang="en", rescale_with_baseline=True)
    ret = bert_scorer.score([sentence1, ], [sentence2, ])[2].item()
    ret = max(ret, 0)
    ret = min(ret, 1)
    return ret

# 入口
def ComprehensionAccuracy( predict_query, gold_query, model_type="roberta-large" ):
    if model_type in ["roberta-large"]:
        return BERTScore_Similarity( predict_query, gold_query, model_type )
    elif model_type in ["text-embedding-ada-002"]:
        return GPT_text_Similarity( predict_query, gold_query )
    
def CA_Batch( predict_query_list, gold_query_list, model_type="roberta-large"):
    if len( predict_query_list ) != len( gold_query_list ):
        raise Exception( f"长度不一致 {len( predict_query_list ), len( gold_query_list )}")
    ca_list = []
    for i in tqdm( range( len(predict_query_list)), desc = "CA Similarity..."  ):
        ca_list.append(  ComprehensionAccuracy( predict_query_list[i], gold_query_list[i], model_type=model_type ) )
    CA = sum( ca_list )*100  / len(ca_list)
    return CA, ca_list


if __name__ == "__main__":
    from wayne_utils import load_data
    total_list = []
    gold_list = []
    gold_result = load_data( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher_data_process/N3_db_construction/inter_queries_dict/0_gold_query_list.json", "json")
    gpt_result = load_data( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher_data_process/N3_db_construction/inter_queries_dict/1_n3_GPT-4.json", "json")
    for key in gpt_result.keys():
        gold_list.extend( gold_result[key] )
        total_list.extend( gpt_result[key] )
    CA, ca_list = CA_Batch( total_list, gold_list )
    print( CA )