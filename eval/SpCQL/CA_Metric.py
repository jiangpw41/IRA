import bert_score
from tqdm import tqdm

def Neo4j_ComprehensionAccuracy( predict_list: list[str], label_list: list[str] ):
    "Comprehension Accuracy: 语义一致准确率"
    if len(predict_list) != len(label_list):
        raise Exception(f"预测结果列表与标签长度不一致：{len(predict_list), len(label_list)}")
    bert_scorer = bert_score.BERTScorer( model_type="roberta-large", lang="en", rescale_with_baseline=True)
    # bert_scorer = bert_score.BERTScorer( model_type="xlm-roberta-large", lang="en", rescale_with_baseline=True)
    sim_list = []
    count = 0
    for pred, tgt in tqdm(zip( predict_list, label_list ), desc=f"Bert Scoring"):
        ret = bert_scorer.score([pred, ], [tgt, ])[2].item()
        ret = max(ret, 0)
        ret = min(ret, 1)
        sim_list.append( ret )
    # 计算正确比例
    CA = sum(sim_list)*100/len(sim_list)
    return float(CA)