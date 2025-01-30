import torch
from bert_score import BERTScorer

bert_scorer = None

def find_most_similar_string(query, string_list):
    """
    使用 BERTScore 找到与 query 最相似的字符串。
    
    :param query: 输入的查询字符串
    :param string_list: 字符串列表
    :return: 最相似的字符串及其相似度
    """
    # 初始化 BERTScorer
    global bert_scorer
    if bert_scorer == None:
        bert_scorer = BERTScorer(model_type="roberta-large", lang="en", rescale_with_baseline=True)
    
    # 计算相似度
    references = string_list
    queries = [query] * len(references)  # 将 query 与列表中每个字符串比较
    P, R, F1 = bert_scorer.score(queries, references)  # 获取相似度分数

    # 获取最相似的字符串及其相似度
    best_index = torch.argmax(F1).item()  # 获取最高 F1 分数对应的索引
    most_similar_string = string_list[best_index]
    similarity_score = F1[best_index].item()

    return most_similar_string, similarity_score


def align_restrict( predict_res, label_res):
    if len(label_res) == 0:
        return predict_res
    aligned_list = []
    for i in range(len(predict_res)):
        pre = predict_res[i]
        if pre in label_res:
            aligned_list.append( pre )
        else:
            most_similar_string, score = find_most_similar_string(pre, label_res)
            aligned_list.append(most_similar_string)
    return aligned_list

def replace_restrict_str( aligned_list, predict_res, predict_res_str, index):
    if len(aligned_list) == 0:
        return "无约束"
    if len( aligned_list) != len(predict_res):
        raise Exception(f"{index}约束值对齐后长度不一致")
    for i in range(len(aligned_list)):
        new_predict_res_str = predict_res_str.replace( predict_res[i], aligned_list[i])
    return new_predict_res_str


def get_kv_string_list( obj ):
    predict_kv_list = []
    if isinstance( obj, dict):
        for key in obj.keys():
            value = obj[key]
            if isinstance( value, dict):
                predict_kv_list.extend( get_kv_string_list( value ) )
            elif isinstance( value, str):
                if key not in ["方向", "路径长度"]:
                    predict_kv_list.append( f"{key}<S>{obj[key]}")
            else:
                raise Exception(f"非字典或字符串")
    elif isinstance( obj, list):
        for dicts in obj:
            predict_kv_list.extend( get_kv_string_list(dicts) )
    else:
        raise Exception(f"非字典或列表")
    return predict_kv_list

def align_kv_string_list( predict_obj, label_kv_list ):
    if len(label_kv_list) == 0:
        return predict_obj
    if isinstance( predict_obj, dict):
        ret_dict = {}
        for key in predict_obj.keys():
            value = predict_obj[key]
            if isinstance( value, dict):
                ret_dict[key] = align_kv_string_list( value, label_kv_list )
            elif isinstance( value, str):
                if key not in ["方向", "路径长度"]:
                    predict_str = f"{key}<S>{predict_obj[key]}"
                    matched_str, score = find_most_similar_string(predict_str, label_kv_list)
                    new_key, new_value = matched_str.split("<S>")[0], matched_str.split("<S>")[1]
                    ret_dict[new_key] = new_value
            else:
                raise Exception(f"非字典或字符串")
        return ret_dict
    elif isinstance( predict_obj, list):
        ret_list = []
        for dicts in predict_obj:
            ret_list.append( get_kv_string_list(dicts) )
        return ret_list
    else:
        raise Exception(f"非字典或列表")



# 对每个键值对，寻找最贴切的键值对进行替换
from tqdm import tqdm
import re

def get_restrict_name( text ):
    # 匹配单引号内的文字
    matches = re.findall(r"'(.*?)'", text)
    # 输出结果
    return matches
def add_other( obj_align, obj_post):
    if isinstance( obj_align, dict):
        if "方向" in obj_post:
            obj_align["方向"] = obj_post["方向"]
        if "路径长度" in obj_post:
            obj_align["路径长度"] = obj_post["路径长度"]
        return obj_align
    elif isinstance( obj_post, list):
        ret_list = []
        for i in range(len(obj_post)):
            ret_list.append( add_other( obj_align[i], obj_post[i]))
        return ret_list
    
def subgraph_align( intention_predict_post, top1_list):
    aligned_intention_list = []
    for index in tqdm( range( len(intention_predict_post)), desc="Align"):
        predict_intention = intention_predict_post[index]
        predict_intention
        # 预测部分
        predict_obj = predict_intention['对象']
        predict_res_str = predict_intention['约束']
        predict_res = get_restrict_name( predict_res_str )
        # 标签部分
        label_intention = top1_list[index]
        label_intention
        label_obj = label_intention['对象']
        label_res = label_intention['约束'] 
        label_res

        # 对齐约束
        aligned_list = align_restrict( predict_res, label_res)
        new_predict_res_str = replace_restrict_str( aligned_list, predict_res, predict_res_str, index)

        # 对齐对象
        label_kv_list = get_kv_string_list( label_obj )
        aligned_predict_obj = align_kv_string_list( predict_obj, label_kv_list )
        new_predict_intention = {
            "对象": aligned_predict_obj,
            "约束":new_predict_res_str,
            "返回形式": predict_intention["返回形式"]
        }
        aligned_intention_list.append( new_predict_intention )
    
    for i in range(len(aligned_intention_list)):
        if isinstance( aligned_intention_list[i]['约束'], list) and aligned_intention_list[i]['约束'] == []:
            aligned_intention_list[i]['约束'] = "无约束"
        obj_align = aligned_intention_list[i]['对象']
        obj_post = intention_predict_post[i]['对象']
        aligned_intention_list[i]['对象']= add_other( obj_align, obj_post)
    
    return aligned_intention_list
    
