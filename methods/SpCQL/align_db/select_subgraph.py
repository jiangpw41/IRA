from embedding_retrieving import Embedding, FAISS
from collections import OrderedDict
from wayne_utils import load_data, save_data
import os
from tqdm import tqdm
import re


def check_key( key, all_query_dict):
    if key in all_query_dict.keys():
        new_key = key+","
        return check_key( new_key, all_query_dict)
    else:
        return key

def merge_key( all_query_dict, query_dict):
    for key in query_dict.keys():
        new_key = check_key( key, all_query_dict)
        all_query_dict[new_key] = query_dict[key]
    return all_query_dict

class Db_instance_retriever():
    def __init__( self, all_query_dict ):
        self.all_query_dict = all_query_dict
        self.embedder = Embedding()
        self.entity_key_embedding = None
        self.embedding_list()

        self.faiss = FAISS( self.entity_key_embedding, list(self.all_query_dict.keys()), topk = 3)
        self.faiss.add_all()

    def embedding_list( self ):
        print( "Embedding all query dict")
        self.entity_key_embedding = self.embedder.embedding( self.all_query_dict )

    # 与子图对齐
    def string_match( self, query ):
        for key in self.all_query_dict.keys():
            if query.lower() in key.lower():
                return key
        return None
    
    def find_subgraph( self, query ):
        top1_list = self.faiss.search( query )
        return top1_list
    
# 三种对象类型，列表33（多个字典），节点字典，路径字典
def get_key( intention_obj):
    ret_list = []
    if isinstance( intention_obj, list):
        for subdict in intention_obj:
            ret_list.extend( get_key( subdict) )
    elif isinstance( intention_obj, dict):
        for key in intention_obj.keys():
            if key not in ["路径长度", "方向"]:
                if key not in ["name", "节点1", "节点2"] and "未知属性" not in key:
                    ret_list.append( key )
                # 纳入值
                value = intention_obj[key]
                if isinstance( value, dict):
                    ret_list.extend( get_key( value) )
                else:
                    if value != "待查询":
                        ret_list.append( value )
    else:
        raise Exception(f"对象格式不对{intention_obj}")
    return ret_list

def get_restrict_name( text ):
    # 匹配单引号内的文字
    matches = re.findall(r"'(.*?)'", text)
    # 输出结果
    return matches

def get_query_dict( lists ):
    query_dict = OrderedDict({})
    for index in range( len(lists) ):
        temp = {}
        # 获取涉及的属性
        intention_restrict = lists[index]['约束']
        res_list = get_restrict_name( intention_restrict )
        intention_obj = lists[index]['对象']
        temp["对象"] = intention_obj
        temp["约束"] = res_list

        obj_hash_key = get_key( intention_obj)
        obj_hash_key.extend( res_list )
        hash_key = ",".join(obj_hash_key)
        if hash_key in query_dict:
            '''if temp != query_dict[ hash_key ]:
                while hash_key in query_dict:
                    hash_key = hash_key + ","
                query_dict[ hash_key ] = temp
            else:
                print(f"{hash_key}字典一致{temp}")'''
            while hash_key in query_dict:
                hash_key = hash_key + ","
            query_dict[ hash_key ] = temp
        else:
            query_dict[ hash_key ] = temp
            

    return query_dict

def get_subgraph_index( input_string, labels_list ):
    for i in range(len(labels_list)):
        label = labels_list[i]
        if label == input_string:
            return i
    return -1

def SelectSubgraph( intention_predict_post, all_query_dict):
    db_retriever = Db_instance_retriever( all_query_dict )
    predict_query_key = get_query_dict( intention_predict_post )        # 2007
    key_list = list(predict_query_key)
    subgraph_list = []
    for i in tqdm( range(len(key_list)), desc="Matching subgraph"):
        key_com = key_list[i]
        related_top3 = db_retriever.find_subgraph( key_com )[:3]
        subgraph_list.append( related_top3 )
    labels_list = list(all_query_dict.keys())
    
    match_index_list = []
    first_match, second_match, third_match = [], [], []
    for i in range(len(subgraph_list)):
        subgraphs = subgraph_list[i]
        subgraphs_1 = get_subgraph_index( subgraphs[0] , labels_list )
        subgraphs_2 = get_subgraph_index( subgraphs[1] , labels_list)
        subgraphs_3 = get_subgraph_index( subgraphs[2] , labels_list)
        match_index_list.append( (subgraphs_1, subgraphs_2, subgraphs_3)) # , 
        if subgraphs_1 == i:
            first_match.append( True )
        else:
            first_match.append( False )
        
        if i in match_index_list[-1][:2]:
            second_match.append( True )
        else:
            second_match.append( False )
        
        if i in match_index_list[-1]:
            third_match.append( True )
        else:
            third_match.append( False )
        
    print(f"Top1匹配率：{sum(first_match)/len(first_match)}")
    print(f"Top2匹配率：{sum(second_match)/len(second_match)}")
    print(f"Top3匹配率：{sum(third_match)/len(third_match)}")

    top1_list = [all_query_dict[subgraph_list[i][0]] for i in range(len(subgraph_list))]
    return top1_list