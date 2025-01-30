from wayne_utils import load_data
from query_parser_nGQL import*
from query_parser_Cypher import parse_match_query
from type_stat import nGQL_classify, get_intention

def get_standard_list( intentions, method):
    ret_list = []
    for i in range( len(intentions)):
        standard = method( intentions[i] )
        ret_list.append(standard )
    return ret_list
    
def trans_fetch_obj( type, objects, label ):
    ret_dict = {}
    ret_dict["type"] = type
    ret_dict["label"] = label
    if type == "vertex":
        ret_dict["names"] = objects
    else:
        ret_dict['nodes'] = objects
    return ret_dict

def parse_fetch_to_standard( intention ):
    temp_result = {
        "query_pattern": "node_or_edge",       # [ "node_or_edge", "relation_or_path", "sub_graph", "modify_db", "other"],        # multi_nodes包含单跳、多条关系，路径，遍历等
        "recommend_keywords": "fetch prop on",      # ["match", "lookup_on", "go from", "fetch prop on", "get subgraph", "find path"],
        "related_objects" : [],
        "restrict": [],
        "return_format": {
            "distinct" : False,
            "return_object": None,
            'order by': None,
            'limit': None,
            'skip': None,
        },
        "clauses": []
    }
    temp_result["related_objects"] = [trans_fetch_obj( intention['target'], intention['object'], intention['tag_or_type'] )]
    temp_result["restrict"] = intention['restrict']
    temp_result["return_format"]["return_object"] = intention['other_yield']
    temp_result["clauses"].extend( intention['other_clause'] )
    return temp_result

label_dicts = load_data( "/home/jiangpeiwen2/jiangpeiwen2/NL2GQL/methods/MyMethod/N3/edge_vertex.json", "json")

def get_label_type( label_dicts, label):
    for space_name in label_dicts.keys():
        for _type in label_dicts[space_name].keys():
            if label in label_dicts[space_name][_type]['name_list']:
                return _type.lower()
    return None

def parse_look_to_standard( intention ):
    temp_result = {
        "query_pattern": "node_or_edge",       # [ "node_or_edge", "relation_or_path", "sub_graph", "modify_db", "other"],        # multi_nodes包含单跳、多条关系，路径，遍历等
        "recommend_keywords": "lookup on",      # ["match", "lookup_on", "go from", "fetch prop on", "get subgraph", "find path"],
        "related_objects" : [],
        "restrict": [],
        "return_format": {
            "distinct" : False,
            "return_object": None,
            'order by': None,
            'limit': None,
            'skip': None,
        },
        "clauses": []
    }
    temp_result["related_objects"] = [{
        "type": get_label_type( label_dicts, intention['tag_or_type']),
        "label": intention['tag_or_type'],
        "properties" : intention['object']
    }]
    temp_result["restrict"] = intention['restrict']
    temp_result["return_format"]["return_object"] = intention['other_yield']
    temp_result["clauses"].extend( intention['other_clause'] )
    return temp_result

def parse_find_to_standard( intention ):
    temp_result = {
        "query_pattern": "relation_or_path",       # [ "node_or_edge", "relation_or_path", "sub_graph", "modify_db", "other"],        # multi_nodes包含单跳、多条关系，路径，遍历等
        "recommend_keywords": "find .. path",      # ["match", "lookup_on", "go from", "fetch prop on", "get subgraph", "find path"],
        "related_objects" : [],
        "restrict": [],
        "return_format": {
            "distinct" : False,
            "return_object": None,
            'order by': None,
            'limit': None,
            'skip': None,
        },
        "clauses": []
    }
    temp_result["related_objects"] = [{
        "type": 'path',
        "start_node" : intention['object'][0]['start_node'],
        "end_node" : intention['object'][0]['end_node'],
        "edge" : intention['object'][0]['edge'],
        "length" : intention['object'][0]['range'],
    }]
    temp_result["restrict"] = intention['restrict']
    temp_result["return_format"]["return_object"] = intention['other_yield']
    temp_result["clauses"].extend( intention['other_clause'] )
    return temp_result

def parse_subgraph_to_standard( intention ):
    temp_result = {
        "query_pattern": "sub_graph",       # [ "node_or_edge", "relation_or_path", "sub_graph", "modify_db", "other"],        # multi_nodes包含单跳、多条关系，路径，遍历等
        "recommend_keywords": "GET SUBGRAPH".lower(),      # ["match", "lookup_on", "go from", "fetch prop on", "get subgraph", "find path"],
        "related_objects" : [],
        "restrict": [],
        "return_format": {
            "distinct" : False,
            "return_object": None,
            'order by': None,
            'limit': None,
            'skip': None,
        },
        "clauses": []
    }
    temp_result["related_objects"] = [{
        "type": 'path',
        "start_node" : intention['object']['start_node'],
        "edge" : intention['object']['edge'],
    }]
    temp_result["restrict"] = intention['restrict']
    temp_result["return_format"]["return_object"] = intention['other_yield']
    temp_result["clauses"].extend( intention['other_clause'] )
    return temp_result

def parse_go_to_standard( intention ):
    temp_result = {
        "query_pattern": "relation_or_path",       # [ "node_or_edge", "relation_or_path", "sub_graph", "modify_db", "other"],        # multi_nodes包含单跳、多条关系，路径，遍历等
        "recommend_keywords": "GO .. FROM".lower(),      # ["match", "lookup_on", "go from", "fetch prop on", "get subgraph", "find path"],
        "related_objects" : [],
        "restrict": [],
        "return_format": {
            "distinct" : False,
            "return_object": None,
            'order by': None,
            'limit': None,
            'skip': None,
        },
        "clauses": []
    }
    temp_result["related_objects"] = [{
        "type": 'path',
        "start_node" : intention['object']['start_node'],
        "edge" : intention['object']['edge'],
    }]
    temp_result["restrict"] = intention['restrict']
    temp_result["return_format"]["return_object"] = intention['other_yield']
    temp_result["clauses"].extend( intention['other_clause'] )
    return temp_result

def parse_wirte_other_to_standard( part_list, type):
    ret_list = []
    for i in range(len(part_list)):
        if type == "write":
            ret_list.append( {
                "query_pattern" : "write"
            })
        else:
            ret_list.append( {
                "query_pattern" : "others"
            })
    return ret_list


def get_single_intention( class_dict ):
    for key in class_dict.keys():
        lists = class_dict[key]
        if lists != []:
            return key, lists[0]
    return None, None

def parse_intention(class_dict ):
    parsed_dict = {
        "WRITE": [],
        "OTHER": []
    }
    query_dict = {
        "WRITE": [],
        "OTHER": []
    }
    for key in class_dict.keys():
        part_list = class_dict[key]
        if key == 'MATCH':                          # 543
            parsed_dict[key] = get_intention( part_list, parse_match_query)
            query_dict[key] = part_list
        elif key == 'FETCH PROP ON':                # +69 = 612
            intentions = get_intention( part_list, parse_fetch_query)
            parsed_dict[key] = get_standard_list( intentions, parse_fetch_to_standard)
            query_dict[key] = part_list
        elif key == 'LOOKUP ON':                    # +106 = 718
            intentions = get_intention( part_list, parse_lookup_query)
            parsed_dict[key] = get_standard_list( intentions, parse_look_to_standard)
            query_dict[key] = part_list
        elif key == 'FIND':                         # +43 = 761
            intentions = get_intention( part_list, parse_find_query)
            parsed_dict[key] = get_standard_list( intentions, parse_find_to_standard)
            query_dict[key] = part_list
        elif key == 'GET SUBGRAPH':                 # +34 = 795
            intentions = get_intention( part_list, parse_subgraph_query)
            parsed_dict[key] = get_standard_list( intentions, parse_subgraph_to_standard)
            query_dict[key] = part_list
        elif key == 'GO':                           # +189 = 984
            intentions = get_intention( part_list, parse_go_query)
            parsed_dict[key] = get_standard_list( intentions, parse_go_to_standard)
            query_dict[key] = part_list
        elif key == 'MIXED':                        # +22 = 1006
            intentions = get_intention( part_list, parse_mixed_to_standard)
            parsed_dict[key] = intentions
            query_dict[key] = part_list
        elif key in ['INSERT', 'OTHER_WRITE'] :                        # +22 = 1006
            parsed_dict["WRITE"].extend( parse_wirte_other_to_standard( part_list, "write") )
            query_dict["WRITE"].extend( part_list )
        else:
            parsed_dict["OTHER"].extend( parse_wirte_other_to_standard( part_list, "other") )
            query_dict["OTHER"].extend( part_list )
        
    return parsed_dict, query_dict