from wayne_utils import load_data, save_data
import os
#共597个nba

# 63
def trans_write_nba( intention ):
    return  "写数据库"

# 543: disease 127, potter 185, nba 225 
def trans_match_nba( intention, index ):
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
    lens = len(intention["related_objects"])
    # 处理单跳跃关系或node
    if lens == 1:
        if intention["related_objects"][0]["type"] == "node":       # node 52
            obj_temp = {
                "category": "node",
                "label": intention['related_objects'][0]["label"],
            }
            if intention['related_objects'][0]["properties"] != None:
                for key in intention['related_objects'][0]["properties"]:
                    obj_temp[key] = intention['related_objects'][0]["properties"][key]
            # 从约束中获取等号
            new_restrict = []
            for rest in intention['restrict']:
                if rest.count("==") == 1:
                    value = intention['restrict'][0].split( "==")[1].strip("\" '")
                    if "name" in intention['restrict'][0]:
                        obj_temp["name"] = value 
                    else:
                        obj_temp["id"] = value
                else:
                    new_restrict.append( rest )
            # 从返回格式中获取等号
            new_aggre = []
            for agg in intention['return_format']["return_object"]:
                if "name" in agg.lower():
                    obj_temp["name"] = "待查询"
                elif "age" in agg.lower():
                    obj_temp["age"] = "待查询"
                for agg_key in ["min", "max", "sum", "collect", "count", "id", "avg", "label", "properties"]:
                    if agg_key in agg.lower() and agg_key not in new_aggre:
                        new_aggre.append( agg_key )
            intention_temp["查询对象"].append( obj_temp )
            intention_temp["查询约束"] = new_restrict
            for key in intention_temp["返回格式"]:
                if key == "aggregation":
                    intention_temp["返回格式"][key] = new_aggre
                else:
                    intention_temp["返回格式"][key] = intention['return_format'][key]
            return intention_temp
        elif intention["related_objects"][0]["type"] == "edge":       # edge 112
            obj_temp = {
                "category": "edge",
                "label": intention['related_objects'][0]["label"],
            }
            if intention['related_objects'][0]["properties"] != None:
                for key in intention['related_objects'][0]["properties"]:
                    obj_temp[key] = intention['related_objects'][0]["properties"][key]
            for _node in ["start_node", "end_node"]:
                obj_temp[_node] = {}
                obj_temp[_node]["label"] = intention['related_objects'][0][_node]["label"]
                if intention['related_objects'][0][_node]["properties"] != None:
                    for key in intention['related_objects'][0][_node]["properties"]:
                        obj_temp[_node][key] = intention['related_objects'][0][_node]["properties"][key]
            # 从约束中获取等号
            new_restrict = []
            for rest in intention['restrict']:
                new_restrict.append( rest )
            # 从返回格式中获取等号
            new_aggre = []
            for agg in intention['return_format']["return_object"]:
                for agg_key in ["min", "max", "sum", "collect", "count", "id", "avg", "label", "type", "concat", "properties"]:
                    if agg_key in agg.lower() and agg_key not in new_aggre:
                        new_aggre.append( agg_key )
            intention_temp["查询对象"].append( obj_temp )
            intention_temp["查询约束"] = new_restrict
            for key in intention_temp["返回格式"]:
                if key == "aggregation":
                    intention_temp["返回格式"][key] = new_aggre
                else:
                    intention_temp["返回格式"][key] = intention['return_format'][key]
            return intention_temp
        elif intention["related_objects"][0]["type"] == "path":       # path 32
            obj_temp = {
                "category": "path",
                "label": intention['related_objects'][0]["label"],
                "length": intention['related_objects'][0]["length"] if "length" in intention['related_objects'][0] else None,
            }
            for _node in ["start_node", "end_node"]:
                obj_temp[_node] = {}
                if _node in intention['related_objects'][0]:
                    obj_temp[_node]["label"] = intention['related_objects'][0][_node]["label"]
                    if intention['related_objects'][0][_node]["properties"] != None:
                        for key in intention['related_objects'][0][_node]["properties"]:
                            obj_temp[_node][key] = intention['related_objects'][0][_node]["properties"][key]
            # 从约束中获取等号
            new_restrict = []
            for rest in intention['restrict']:
                if rest.count("==") == 1:
                    if "length" in rest:
                        obj_temp["length"] = rest.split("==")[1].strip()
                new_restrict.append( rest )
            # 从返回格式中获取等号
            new_aggre = []
            for agg in intention['return_format']["return_object"]:
                if "likeness" in agg:
                    obj_temp["likeness"] = "待查询"
                if "length" in agg:
                    obj_temp["length"] = "待查询"
                for agg_key in ["min", "max", "sum", "collect", "count", "id", "avg", "label", "type", "concat", "relationships", "properties"]:
                    if agg_key in agg.lower() and agg_key not in new_aggre:
                        new_aggre.append( agg_key )
            intention_temp["查询对象"].append( obj_temp )
            intention_temp["查询约束"] = new_restrict
            for key in intention_temp["返回格式"]:
                if key == "aggregation":
                    intention_temp["返回格式"][key] = new_aggre
                else:
                    intention_temp["返回格式"][key] = intention['return_format'][key]
            return intention_temp
    else:
        for i in range(lens):
            obj_temp = {
                "category": "edge",
                "label": intention['related_objects'][i]["label"],
            }
            for _node in ["start_node", "end_node"]:
                obj_temp[_node] = {}
                if _node in intention['related_objects'][i]:
                    obj_temp[_node]["label"] = intention['related_objects'][i][_node]["label"]
                    if intention['related_objects'][i][_node]["properties"] != None:
                        for key in intention['related_objects'][i][_node]["properties"]:
                            obj_temp[_node][key] = intention['related_objects'][i][_node]["properties"][key]
            # 从约束中获取等号
            new_restrict = intention['restrict']
            # 从返回格式中获取等号
            new_aggre = []
            for agg in intention['return_format']["return_object"]:
                if "likeness" in agg:
                    obj_temp["likeness"] = "待查询"
                if "length" in agg:
                    obj_temp["length"] = "待查询"
                for agg_key in ["min", "max", "sum", "collect", "count", "id", "avg", "label", "type", "concat", "relationships", "properties"]:
                    if agg_key in agg.lower() and agg_key not in new_aggre:
                        new_aggre.append( agg_key )
            intention_temp["查询对象"].append( obj_temp )
        intention_temp["查询约束"] = new_restrict
        for key in intention_temp["返回格式"]:
            if key == "aggregation":
                intention_temp["返回格式"][key] = new_aggre
            else:
                intention_temp["返回格式"][key] = intention['return_format'][key]
        return intention_temp
    return "错误"

# 69: disease 4, nba 61)
def trans_fetch_nba( intention, index ):
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
    if intention['related_objects'][0]["type"] == "vertex":
        obj_temp = {
            "category": "node",
            "label": intention['related_objects'][0]["label"],
            'node_id_list': intention['related_objects'][0]['names'],
        }
    else:
        obj_temp = {
            "category": "edge",
            "label": intention['related_objects'][0]["label"],
            'start_node_id_list': [],
            'end_node_id_list': [],
        }
        for item in intention['related_objects'][0]["nodes"]:
            obj_temp['start_node_id_list' ].append( item['start_node'])
            obj_temp['end_node_id_list' ].append( item['end_node'])
    # 从约束中获取等号
    new_restrict = []
    # 从返回格式中获取等号
    new_aggre = []
    for agg in intention['return_format']["return_object"]:
        if "待查询" in agg:
            key = agg.split(":")[0].strip()
            obj_temp[key] = "待查询"
        for agg_key in ["min", "max", "sum", "collect", "count", "id", "avg", "label", "type", "concat", "properties"]:
            if agg_key in agg.lower() and agg_key not in new_aggre:
                new_aggre.append( agg_key )
    intention_temp["查询对象"].append( obj_temp )
    intention_temp["查询约束"] = new_restrict
    for key in intention_temp["返回格式"]:
        if key == "aggregation":
            intention_temp["返回格式"][key] = new_aggre
        else:
            intention_temp["返回格式"][key] = intention['return_format'][key]
    return intention_temp

# 106: disease 28, potter 21, nba 47
def trans_lookup_nba( intention, query, index ):
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
        "category": "node" if "t1" in query or "player" in query else "edge",
        "label": [intention["related_objects"][0]["label"]],
    }
    for key in intention['related_objects'][0]['properties']:
        value = intention['related_objects'][0]['properties'][key]
        obj_temp[key] = value
    # 从约束中获取等号
    new_restrict = intention["restrict"]
    # 从返回格式中获取等号
    new_aggre = []
    for agg in intention['return_format']["return_object"]:
        if "src(" in agg:
            obj_temp["start_node"] = "待查询"
        if "dst(" in agg:
            obj_temp["end_node"] = "待查询"
        if "rank(" in agg:
            obj_temp["rank"] = "待查询"
        if "id" in agg:
            obj_temp["id"] = "待查询"
        for agg_key in ["min", "max", "sum", "collect", "count", "id", "avg", "label", "type", "concat", "properties"]:
            if agg_key in agg.lower() and agg_key not in new_aggre:
                new_aggre.append( agg_key )
    intention_temp["查询对象"].append( obj_temp )
    intention_temp["查询约束"] = new_restrict
    for key in intention_temp["返回格式"]:
        if key == "aggregation":
            intention_temp["返回格式"][key] = new_aggre
        else:
            intention_temp["返回格式"][key] = intention['return_format'][key]
    return intention_temp

# 43 (disease 0, potter 7, nba 36)
def trans_find_nba( intention, index ):
    intention_temp = {
        "查询对象":[{
            "category": "path",
            'start_node_id_list': intention['related_objects'][0]['start_node'],
            'end_node_id_list': intention['related_objects'][0]['end_node'],
            'edge_type_list': intention['related_objects'][0]['edge'],
            "length": intention['related_objects'][0]['length'],
            "have_direction": True
        }],
        "查询约束":[intention["restrict"]],
        "返回格式":{
            "distinct": None,
            "aggregation": [],
            "order by": None,
            "limit": None,
            "skip": None
        }
    }
    new_edges = []
    for edge in intention_temp["查询对象"][0]['edge_type_list']:
        if "," in edge:
            edge1, edge2 = edge.split(",")[0].strip(), edge.split(",")[1].strip()
            new_edges.append( edge1)
            new_edges.append( edge2)
        else:
            new_edges.append( edge)
    intention_temp["查询对象"][0]['edge_type_list'] = new_edges
    return intention_temp

# 34 (disease 11, potter 7, nba 16)
def trans_subgraph_nba( intention, index ):
    intention_temp = {
        "查询对象":[{
            "category": "sub_graph",
            'start_node_id_list': intention['related_objects'][0]['start_node'],
            'edge_type_list': [],
        }],
        "查询约束":intention["restrict"],
        "返回格式":{
            "distinct": None,
            "aggregation": [],
            "order by": None,
            "limit": None,
            "skip": None
        }
    }
    for key in intention['related_objects'][0]["edge"]:
        for edge in intention['related_objects'][0]["edge"][key]:
            if edge not in intention_temp["查询对象"][0]['edge_type_list']:
                intention_temp["查询对象"][0]['edge_type_list'].append(edge)
    return intention_temp

# 189 (disease 51, potter 11, nba 127)
def trans_go_nba( intention,  index ):
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
        "category": "path",
        'start_node_id_list': intention['related_objects'][0]['start_node'],
        'edge_type_list': [],
        "length": None,
        "have_direction": True
    }
    for key in intention['related_objects'][0]["edge"]:
        for edge in intention['related_objects'][0]["edge"][key]:
            if edge not in obj_temp['edge_type_list']:
                obj_temp['edge_type_list'].append(edge)
    # 从约束中获取等号
    new_restrict = []
    for res in intention["restrict"]:
        if "steps" in res:
            obj_temp["length"] = res
        else:
            new_restrict.append(res)
    # 从返回格式中获取等号
    new_aggre = []
    for agg in intention['return_format']["return_object"]:
        if "dst(" in agg:
            obj_temp["end_node"] = "待查询"

        for agg_key in ["min ", "max", "sum", "collect", "count", "id", "avg", "label", "type", "concat", "properties"]:
            if agg_key in agg.lower() and agg_key not in new_aggre:
                new_aggre.append( agg_key.strip() )
    intention_temp["查询对象"].append( obj_temp )
    intention_temp["查询约束"] = new_restrict
    for key in intention_temp["返回格式"]:
        if key == "aggregation":
            intention_temp["返回格式"][key] = new_aggre
        else:
            intention_temp["返回格式"][key] = intention['return_format'][key]
    return intention_temp

def main( work_dir ):
    # nba_write
    nba_write_intention_list_raw = load_data( os.path.join( work_dir, "nba-write_intention_list_raw.json"), "json")
    nba_write_intention = []
    for i in range( len(nba_write_intention_list_raw)):
        nba_write_intention.append( trans_write_nba( nba_write_intention_list_raw[i]))
    save_data( nba_write_intention, os.path.join( work_dir, "nba-write_intention_list.json"))

    # nba_match
    nba_match_intention_list_raw = load_data( os.path.join( work_dir, "nba-match_intention_list_raw.json"), "json")
    nba_match_intention = []
    for i in range( len(nba_match_intention_list_raw)):
        nba_match_intention.append( trans_match_nba( nba_match_intention_list_raw[i],  i ))
    save_data( nba_match_intention, os.path.join( work_dir, "nba-match_intention_list.json"))

    # nba_fetch
    nba_fetch_intention_list_raw = load_data( os.path.join( work_dir, "nba-fetch_intention_list_raw.json"), "json")
    nba_fetch_intention = []
    for i in range( len(nba_fetch_intention_list_raw)):
        nba_fetch_intention.append( trans_fetch_nba( nba_fetch_intention_list_raw[i], i ))
    save_data( nba_fetch_intention, os.path.join( work_dir, "nba-fetch_intention_list.json"))

    # nba_lookup
    nba_lookup_intention_list_raw = load_data( os.path.join( work_dir, "nba-lookup_intention_list_raw.json"), "json")
    query_list = load_data( os.path.join( work_dir, "nba-lookup_query_list.json"), "json")
    nba_lookup_intention = []
    for i in range( len(nba_lookup_intention_list_raw)):
        nba_lookup_intention.append( trans_lookup_nba( nba_lookup_intention_list_raw[i], query_list[i], i ))
    save_data( nba_lookup_intention, os.path.join( work_dir, "nba-lookup_intention_list.json"))

    # nba_find
    nba_find_intention_list_raw = load_data( os.path.join( work_dir, "nba-find_intention_list_raw.json"), "json")
    nba_find_intention = []
    for i in range( len(nba_find_intention_list_raw)):
        nba_find_intention.append( trans_find_nba( nba_find_intention_list_raw[i], i ))
    save_data( nba_find_intention, os.path.join( work_dir, "nba-find_intention_list.json"))

    # nba_subgraph
    nba_subgraph_intention_list_raw = load_data( os.path.join( work_dir, "nba-subgraph_intention_list_raw.json"), "json")
    nba_subgraph_intention = []
    for i in range( len(nba_subgraph_intention_list_raw)):
        nba_subgraph_intention.append( trans_subgraph_nba( nba_subgraph_intention_list_raw[i], i ))
    save_data( nba_subgraph_intention, os.path.join( work_dir, "nba-subgraph_intention_list.json"))

    # nba_go
    nba_go_intention_list_raw = load_data( os.path.join( work_dir, "nba-go_intention_list_raw.json"), "json")
    nba_go_intention = []
    for i in range( len(nba_go_intention_list_raw)):
        nba_go_intention.append( trans_go_nba( nba_go_intention_list_raw[i], i ))
    save_data( nba_go_intention, os.path.join( work_dir, "nba-go_intention_list.json"))


if __name__ == "__main__":
    work_dir = "/home/jiangpeiwen2/jiangpeiwen2/NL2GQL/methods/MyMethod/N3/intentions/intention_extract/nba"
    # main( work_dir )
    
    
    