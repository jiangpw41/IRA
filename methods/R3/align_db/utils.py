
def aligned_or_not( intention_predicts_list,intention_labels_list ):
    aligned_list = []       # 212 / 1254
    not_aligned_list = []

    query_pattern = []
    recommend_keywords = []
    related_objects = []
    restrict = []
    return_format = []
    clauses = []
    for i in range(len(intention_predicts_list)):
        try:
            _label = intention_labels_list[i]
            _predict = intention_predicts_list[i]
            if _predict == _label:
                aligned_list.append( i )
            else:
                try:
                    not_aligned_list.append( i )
                    
                    if "查询约束" in _predict and _predict["查询约束"] != _label["查询约束"]:
                        restrict.append( i )
                    if "查询对象" in _predict and _predict["查询对象"] != _label["查询对象"]:
                        related_objects.append( i )
                    if "返回格式" in _predict and _predict["返回格式"] != _label["返回格式"]:
                        return_format.append( i )
                except KeyError:
                    raise Exception( f"{_label}, {_predict}")
        except:
            raise Exception(f"{i}: {_label}")
    
    print( f"总数{ len(intention_predicts_list)}，完全一致数量{len(aligned_list)}")
    print( f"查询对象一致数量{ len(intention_predicts_list) - len(related_objects)}，")
    print( f"查询约束一致数量{ len(intention_predicts_list) - len(restrict)}，")
    print( f"返回格式一致数量{ len(intention_predicts_list) - len(return_format)}，")
    return not_aligned_list, related_objects, restrict, return_format

def obj_type_diff( intention_labels_list, intention_predicts_list):
    """
    predict : {'node': 378, 'edge': 365, 'path': 412} // {1: 1155, 2: 83, 0: 8, 3: 8}
    """
    lens, types = [], []
    for i in range( len(intention_labels_list) ):
        _label = intention_labels_list[i]["related_objects"]
        if "related_objects" not in intention_predicts_list[i]:
            lens.append( i )
            continue
        _predict = intention_predicts_list[i]["related_objects"]
        if len(_label) != len(_predict):
            lens.append(i)
        else:
            flag = 0
            for j in range( len(_label) ):
                dict_label, dict_predict = _label[j], _predict[j]
                try:
                    if "type" in dict_predict and dict_label["type"] != dict_predict["type"]:
                        flag = 1
                        break
                except:
                    raise Exception( dict_predict )
            if flag == 1:
                types.append(i)
    print( f"对象列表长度不一致的有: {len(lens)}个，长度一致但type不一致的有 {len(types)}")
    return lens, types

import os
os.chdir( "/home/jiangpeiwen2/jiangpeiwen2/NL2GQL/exec_post" )
from nebula_execute import DB_execute
from tqdm import tqdm

def get_all_node_name( space_name ):
    """统计空间内所有节点、边数量
    executor.exec( "SUBMIT JOB STATS;")
    executor.exec( "SHOW STATS;")
    """
    executor = DB_execute(space_name)
    tag_id_dict = {}
    tags_result = executor.exec("SHOW TAGS")
    tags = [tag.values()[0].as_string() for tag in list(tags_result )]
    for i in tqdm( range(len(tags)), desc=f""):
        tag = tags[i]
        node_vid_list = executor.exec(f"MATCH (v:{tag}) RETURN id(v);")
        node_name = list(node_vid_list)
        tag_id_dict[tag] = node_name
        
    return tag_id_dict


def statistic_obj_len( lists ):
    """是否存在'related_objects'键，值是否为列表，列表长度分布
    label: {0: 8, 1: 1155, 2: 83, 3: 8}
    predict: {0: 13, 1: 1150, 2: 88, 3: 3}   not_ex = 13, 
    """
    lens_dict = { 0:0, 1:0}
    not_list = []
    not_ex = []
    for i in range(len(lists)):
        _dict = lists[i]
        if 'related_objects' not in _dict:
            lens_dict[0] += 1
            not_ex.append(i)
        else:
            if isinstance( _dict['related_objects'], list ):
                _len = len(_dict['related_objects'])
                if _len not in lens_dict:
                    lens_dict[_len] = 0
                lens_dict[_len] += 1
            else:
                lens_dict[1] += 1
                not_list.append(i)
    return lens_dict, not_list, not_ex