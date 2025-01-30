

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import bert_score
from tqdm import tqdm
import jieba

bert_scorer = None

def jaccard_similarity(set1, set2):
    set1 = set(set1)
    set2 = set(set2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def compute_tfidf_vectors(sentences):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    tfidf_vectors = tfidf_matrix.toarray()
    return tfidf_vectors
    

def compute_bm25_similarity(tfidf_vectors, k1=1.5, b=0.75):
    doc1_tf = tfidf_vectors[0]
    doc2_tf = tfidf_vectors[1]
    doc_len = np.sum(doc1_tf)  # Total term count in the document
    doc_len_avg = np.mean(np.sum(tfidf_vectors, axis=1))  # Average document length

    idf = np.log((len(tfidf_vectors) + 1) / (np.count_nonzero(tfidf_vectors, axis=0) + 1)) + 1
    idf[idf < 0] = 0  # Replace negative idf values with 0

    bm25_sim = np.sum((doc1_tf * (k1 + 1)) / (doc1_tf + k1 * (1 - b + b * doc_len / doc_len_avg)) * doc2_tf * idf)

    return bm25_sim

def bm25_similarity(sentence1, sentence2):
    # 分词
    tokens1 = jieba.lcut(sentence1.lower())
    tokens2 = jieba.lcut(sentence2.lower())

    # 计算Jaccard相似度
    jaccard_sim = jaccard_similarity(tokens1, tokens2)

    # 计算BM25相似度
    combined_sentences = [sentence1, sentence2]
    try:
        tfidf_vectors = compute_tfidf_vectors(combined_sentences)   # Compute TF-IDF vectors
    except ValueError as e:
        print(f"警告：无法计算TF-IDF向量。输入句子：'{sentence1}' 和 '{sentence2}'")
        return 0.0
    bm25_sim = compute_bm25_similarity(tfidf_vectors)           # Compute BM25 similarity

    # Normalize the similarities
    jaccard_sim = jaccard_sim / 1.0  # Jaccard similarity is already in [0, 1]
    bm25_sim = (bm25_sim + 1) / 2.0  # Normalize BM25 similarity to [0, 1]

    # Combine TF-IDF, BM25, and Jaccard using weighted sum
    combined_sim = (0.5 * jaccard_sim) + (0.3 * bm25_sim) + (0.2 * tfidf_vectors[0].dot(tfidf_vectors[1]))
    return combined_sim

def calculate_bert_score(sentence1, sentence2, model_type='bert-base-multilingual-cased'):
    global bert_scorer
    if bert_scorer == None:
        bert_scorer = bert_score.BERTScorer( model_type=model_type )
    P, R, F1 = bert_scorer.score([sentence1], [sentence2])
    bert_score_value = F1.item()
    return bert_score_value

def R3_ExecuteAccuracy( predict_result, gold_result, syntax_score ):
    if syntax_score == 1 and not predict_result.endswith("错误"):
        if str(predict_result) == str(gold_result):
            bert_score_temp = 1
            bm25_score_temp = 1
        else:
            bert_score_temp = calculate_bert_score(predict_result,gold_result)
            bm25_score_temp = bm25_similarity( str(predict_result), str(gold_result))
    else:
        bm25_score_temp = 0
        bert_score_temp = 0
    avg_score = (bm25_score_temp + bert_score_temp) / 2
    return avg_score

def Neo4j_ExecutionAccuracy_R3( predict_result_list, gold_result_list, syntax_score_list ):
    if len( predict_result_list ) != len( gold_result_list ) or \
        len( predict_result_list ) != len( syntax_score_list ) or \
        len( gold_result_list ) != len( syntax_score_list ):
        raise Exception( f"三者长度不一致{ len( predict_result_list ), len( gold_result_list ), len( syntax_score_list )}")
    R3_EA_list = []
    IEA_list = []
    for i in tqdm( range( len(predict_result_list) ), desc="R3 EA evaluating..." ):
        result = R3_ExecuteAccuracy( str(predict_result_list[i]), str(gold_result_list[i]), syntax_score_list[i] )
        R3_EA_list.append( result )
        if syntax_score_list[i]:
            IEA_list.append( result )
    EA = sum( R3_EA_list )*100 / len( R3_EA_list )
    IEA = sum( IEA_list )*100 / len( IEA_list )
    return EA, IEA