from wayne_utils import load_data, save_data
import os
#共221个disease

# 543: disease 127
def trans_match_disease( intention, index ):
    intention_temp = {
        "查询对象":[],
        "查询约束":[],
        "返回格式":{
            "distinct": None,
            "aggregation": [],
            "order by": None,
            "limit": None,
            "skip": None
        }
    }
    # 处理本来就是节点的简单对象
    if intention['related_objects'][0]['type'] == 'node':   # 有一个没采集好的空情况
        if index == 62:
            obj_temp = {
                "category": "node",
                "label": ["disease"],
                "cure": "物理治疗"
            }
        else:
            obj_temp = {
                "category": "node",
                "label": [intention['related_objects'][0]['label'][0]],
            }
            for key in intention['related_objects'][0]['properties']:
                obj_temp[key] = intention['related_objects'][0]['properties'][key]
        
    else:
        # 特殊处理两个disease之间的非edge关系，即使用同一类药物
        if index == 12:
            obj_temp = {
                "category": "path",
                "label": [],
                "start_node": {
                    "label": ["disease"],
                    "name": "心脏病",
                    "drug": "<相关>"
                },
                "end_node": {
                    "label": ["disease"],
                    "name": "待查询",
                    "drug": "<相关>"
                },
                "length": None,
                "have_direction": False
            }
        else:
            # 起点
            start_label = "disease"
            if intention['related_objects'][0]["start_node"]["properties"] != None:
                start_value = intention['related_objects'][0]["start_node"]["properties"]['name']
            else:
                start_value = "待查询"
            # 终点
            if len(intention['related_objects'][0]["end_node"]['label']) != 1:
                if index == 73:
                    end_label = "department"
                    end_value = "耳鼻喉科"
                elif index == 9:
                    end_label = "cure"
                    end_value = "待查询"
                else:
                    raise Exception(f"其他不合法的intention{intention['related_objects'][0]}")
            else:
                end_label = intention['related_objects'][0]["end_node"]['label'][0]
                end_value = intention['related_objects'][0]["end_node"]["properties"]['name']
            
            # 如果起点终点都是disease，说明是accompany关系
            if start_label == end_label:  # 两个点都是disease，说明是伴生关系
                obj_temp = {
                    "category": "edge",
                    "label": ["accompany_with"],
                    "start_node": {
                        "label": [start_label],
                        "name": start_value
                    },
                    "end_node": {
                        "label": [end_label],
                        "name": end_value
                    },
                    "have_direction": True
                }
            # 否则抽象化为单节点属性
            else:
                obj_temp = {
                    "category": "node",
                    "label": ["disease"],
                    "name": start_value,
                    end_label: end_value
                }
    intention_temp["查询对象"].append( obj_temp )
    if len(intention['return_format']["return_object"]) > 0 and "count" in intention['return_format']["return_object"][0]:
        intention_temp[ "返回格式" ][ "aggregation" ].append( "count()")
    return intention_temp

# 69 ( disease 4)
def trans_fetch_disease( intention, index ):
    intention_temp = {
        "查询对象":[],
        "查询约束":[],
        "返回格式":{
            "distinct": None,
            "aggregation": [],
            "order by": None,
            "limit": None,
            "skip": None
        }
    }
    obj_temp = {
        "category": "node",
        "label": ["disease"],
        "name": intention['related_objects'][0]['names'][0],
        "cured_prob": "待查询"
    }
    intention_temp["查询对象"].append( obj_temp )
    return intention_temp

# 106 (disease 28)
def trans_lookup_disease( intention, index ):
    intention_temp = {
        "查询对象":[],
        "查询约束":[],
        "返回格式":{
            "distinct": None,
            "aggregation": [],
            "order by": None,
            "limit": None,
            "skip": None
        }
    }
    obj_temp = {
        "category": "node",
        "label": ["disease"],
        
    }
    for key in intention['related_objects'][0]['properties']:
        value = intention['related_objects'][0]['properties'][key]
        obj_temp[key] = value
    intention_temp["查询对象"].append( obj_temp )
    return intention_temp

# 34 (disease 11)
def trans_subgraph_disease( intention, index ):
    intention_temp = {
        "查询对象":[{
            "category": "sub_graph",
            'start_node_id_list': intention['related_objects'][0]['start_node'],
            'edge_type_list': None,
        }],
        "查询约束":[ "1 steps" ],
        "返回格式":{
            "distinct": None,
            "aggregation": [],
            "order by": None,
            "limit": None,
            "skip": None
        }
    }
    return intention_temp

# 189 (disease 51)
def trans_go_disease( intention, query,  index ):
    def get_edge( query):
        return query.split("OVER")[1].split("YIELD")[0].strip()
    intention_temp = {
        "查询对象":[{
            "category": "path",
            'start_node_id_list': intention['related_objects'][0]['start_node'],
            'end_node_id_list': "待查询",
            'edge_type_list': [get_edge( query)],
            "length": None,
            "have_direction": True
        }],
        "查询约束":[],
        "返回格式":{
            "distinct": None,
            "aggregation": [],
            "order by": None,
            "limit": None,
            "skip": None
        }
    }
    return intention_temp

def main( work_dir ):
    # disease_match
    disease_match_intention_list_raw = load_data( os.path.join( work_dir, "disease-match_intention_list_raw.json"), "json")
    disease_match_intention = []
    for i in range( len(disease_match_intention_list_raw)):
        disease_match_intention.append( trans_match_disease( disease_match_intention_list_raw[i], i ))
    save_data( disease_match_intention, os.path.join( work_dir, "disease-match_intention_list.json"))

    # disease_fetch
    disease_fetch_intention_list_raw = load_data( os.path.join( work_dir, "disease-fetch_intention_list_raw.json"), "json")
    disease_fetch_intention = []
    for i in range( len(disease_fetch_intention_list_raw)):
        disease_fetch_intention.append( trans_fetch_disease( disease_fetch_intention_list_raw[i], i ))
    save_data( disease_fetch_intention, os.path.join( work_dir, "disease-fetch_intention_list.json"))

    # disease_lookup
    disease_lookup_intention_list_raw = load_data( os.path.join( work_dir, "disease-lookup_intention_list_raw.json"), "json")
    disease_lookup_intention = []
    for i in range( len(disease_lookup_intention_list_raw)):
        disease_lookup_intention.append( trans_lookup_disease( disease_lookup_intention_list_raw[i], i ))
    save_data( disease_lookup_intention, os.path.join( work_dir, "disease-lookup_intention_list.json"))

    # disease_subgraph
    disease_subgraph_intention_list_raw = load_data( os.path.join( work_dir, "disease-subgraph_intention_list_raw.json"), "json")
    disease_subgraph_intention = []
    for i in range( len(disease_subgraph_intention_list_raw)):
        disease_subgraph_intention.append( trans_subgraph_disease( disease_subgraph_intention_list_raw[i], i ))
    save_data( disease_subgraph_intention, os.path.join( work_dir, "disease-subgraph_intention_list.json"))

    # disease_go
    disease_go_intention_list_raw = load_data( os.path.join( work_dir, "disease-go_intention_list_raw.json"), "json")
    go_query_list = load_data( os.path.join( work_dir, "disease-go_query_list.json"), "json" )
    disease_go_intention = []
    for i in range( len(disease_go_intention_list_raw)):
        disease_go_intention.append( trans_go_disease( disease_go_intention_list_raw[i], go_query_list[i], i ))
    save_data( disease_go_intention, os.path.join( work_dir, "disease-go_intention_list.json"))


if __name__ == "__main__":
    work_dir = "/home/jiangpeiwen2/jiangpeiwen2/NL2GQL/methods/MyMethod/N3/intentions/intention_extract/disease"
    main( work_dir )
    