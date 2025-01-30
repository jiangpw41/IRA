from wayne_utils import load_data, save_data
import os
#共231个potter

# 543: disease 127, potter 185
def trans_match_potter( intention, query, index ):
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
    # 处理本来就是节点的简单对象, 61
    if intention['related_objects'][0]['type'] == 'node':
        obj_temp = {
            "category": "node",
            "label": ["character"],
        }
        for key in intention['related_objects'][0]['properties']:
            obj_temp[key] = intention['related_objects'][0]['properties'][key]
    else:
        # 特殊处理kindred关系，即使亲属
        kindred_type = None
        for _ty in ["妹妹", "儿子", "弟弟", "养子", "父亲", "兄妹", "岳父", "姐姐", "养女", "嫂子", "妻子"]:
            if _ty in query.lower():
                kindred_type = _ty
                break
        if "kindred" not in query.lower() and kindred_type!=None:  # 非明面上的亲属关系, 12
            obj_temp = {
                "category": "edge",
                "label": ["kindred"],
                "rel_type": intention['restrict'][0].split("==")[1].strip(),
                "start_node": {
                    "label": ["character"],
                    "name": intention['related_objects'][0]["start_node"]["properties"]["name"],
                },
                "end_node": {
                    "label": ["character"],
                },
                "have_direction": False
            }
        elif "kindred" in query.lower():                          # 明面上的亲属，37
            obj_temp = {
                "category": "edge",
                "label": ["kindred"],
                "rel_type": intention['related_objects'][0]["properties"]["rel_type"],
                "start_node": {
                    "label": ["character"],
                    "name": intention['related_objects'][0]["start_node"]["properties"]["name"],
                },
                "end_node": {
                    "label": ["character"],
                },
                "have_direction": False
            }
            if "n1.character.name" in query:
                obj_temp["end_node"]["name"] = "待查询"
            elif "n1.character.blood" in query:
                obj_temp["end_node"]["blood"] = "待查询"
        else:                                                     # 非亲属，75
            obj_temp = {
                "category": "edge",
                "label": intention['related_objects'][0]["label"],
                "start_node": {
                    "label": ["character"],
                },
                "end_node": {
                    "label": intention['related_objects'][0]["end_node"]["label"],
                },
                "have_direction": False
            }
            if intention['related_objects'][0]["start_node"]["properties"] != None:  
                obj_temp["start_node"]["name"] = intention['related_objects'][0]["start_node"]["properties"]["name"]
            if "n1.college.name" in query or "n1.character.name" in query:      # 如果query有返回后缀而非整体
                obj_temp["end_node"]["name"] = "待查询"
    intention_temp["查询对象"].append( obj_temp )
    if len(intention['return_format']["return_object"]) > 0 and "count" in intention['return_format']["return_object"][0]:
        intention_temp[ "返回格式" ][ "aggregation" ].append( "count()")
    if "LIMIT" in query:
         intention_temp[ "返回格式" ]["limit"] = query.split("LIMIT")[1].strip()
    return intention_temp

# 106: disease 28, potter 21
def trans_lookup_potter( intention, index ):
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
        "label": "character",
    }
    for key in intention['related_objects'][0]['properties']:
        value = intention['related_objects'][0]['properties'][key]
        obj_temp[key] = value
    intention_temp["查询对象"].append( obj_temp )
    return intention_temp

# 43 (disease 0, potter 7)
def trans_find_potter( intention, index ):
    intention_temp = {
        "查询对象":[{
            "category": "path",
            'start_node_id_list': intention['related_objects'][0]['start_node'],
            'end_node_id_list': intention['related_objects'][0]['end_node'],
            'edge_type_list': ["*"],
            "length": "shortest",
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

# 34 (disease 11, potter 7)
def trans_subgraph_potter( intention, index ):
    intention_temp = {
        "查询对象":[{
            "category": "sub_graph",
            'start_node_id_list': intention['related_objects'][0]['start_node'],
            'edge_type_list': None,
        }],
        "查询约束":[ "2 steps" ],
        "返回格式":{
            "distinct": None,
            "aggregation": [],
            "order by": None,
            "limit": None,
            "skip": None
        }
    }
    return intention_temp

# 189 (disease 51, potter 11)
def trans_go_potter( intention,  index ):
    intention_temp = {
        "查询对象":[{
            "category": "path",
            'start_node_id_list': intention['related_objects'][0]['start_node'],
            'end_node_id_list': "待查询",
            'edge_type_list': ["kindred"],
            "length": "2 steps",
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
    # potter_match
    potter_match_intention_list_raw = load_data( os.path.join( work_dir, "potter-match_intention_list_raw.json"), "json")
    match_query_list = load_data( os.path.join( work_dir, "potter-match_query_list.json"), "json" )
    potter_match_intention = []
    for i in range( len(potter_match_intention_list_raw)):
        potter_match_intention.append( trans_match_potter( potter_match_intention_list_raw[i], match_query_list[i],  i ))
    save_data( potter_match_intention, os.path.join( work_dir, "potter-match_intention_list.json"))

    # potter_lookup
    potter_lookup_intention_list_raw = load_data( os.path.join( work_dir, "potter-lookup_intention_list_raw.json"), "json")
    potter_lookup_intention = []
    for i in range( len(potter_lookup_intention_list_raw)):
        potter_lookup_intention.append( trans_lookup_potter( potter_lookup_intention_list_raw[i], i ))
    save_data( potter_lookup_intention, os.path.join( work_dir, "potter-lookup_intention_list.json"))

    # potter_find
    potter_find_intention_list_raw = load_data( os.path.join( work_dir, "potter-find_intention_list_raw.json"), "json")
    potter_find_intention = []
    for i in range( len(potter_find_intention_list_raw)):
        potter_find_intention.append( trans_find_potter( potter_find_intention_list_raw[i], i ))
    save_data( potter_find_intention, os.path.join( work_dir, "potter-find_intention_list.json"))

    # potter_subgraph
    potter_subgraph_intention_list_raw = load_data( os.path.join( work_dir, "potter-subgraph_intention_list_raw.json"), "json")
    potter_subgraph_intention = []
    for i in range( len(potter_subgraph_intention_list_raw)):
        potter_subgraph_intention.append( trans_subgraph_potter( potter_subgraph_intention_list_raw[i], i ))
    save_data( potter_subgraph_intention, os.path.join( work_dir, "potter-subgraph_intention_list.json"))

    # potter_go
    potter_go_intention_list_raw = load_data( os.path.join( work_dir, "potter-go_intention_list_raw.json"), "json")
    potter_go_intention = []
    for i in range( len(potter_go_intention_list_raw)):
        potter_go_intention.append( trans_go_potter( potter_go_intention_list_raw[i], i ))
    save_data( potter_go_intention, os.path.join( work_dir, "potter-go_intention_list.json"))


if __name__ == "__main__":
    work_dir = "/home/jiangpeiwen2/jiangpeiwen2/NL2GQL/methods/MyMethod/N3/intentions/intention_extract/potter"
    # main( work_dir )
    