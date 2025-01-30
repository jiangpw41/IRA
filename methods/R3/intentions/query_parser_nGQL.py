import re
from collections import defaultdict

def split_ngql(query):
    # 定义nGQL关键字
    keywords = [ 'INSERT', 'LOOKUP ON', 'FIND', 'UNWIND', 'MATCH', "GET SUBGRAPH", "GO", 'YIELD', 'RETURN', 'FETCH PROP ON', 'WHERE', 'LIMIT', 'ORDER BY']
    
    # 构造一个正则表达式，用于匹配各个关键字以及它们后面的部分
    # \s*表示任意空白字符（包括空格、换行符），|表示“或者”，\b表示单词边界，确保匹配独立的关键字
    pattern = r'\b(' + '|'.join(keywords) + r')\b\s*(.*?)(?=\s*\b(' + '|'.join(keywords) + r')\b|\s*$)'

    # 查找所有匹配的关键字及其后续部分
    matches = re.findall(pattern, query.replace("\n", " "), flags=re.IGNORECASE)

    # 将匹配结果构造成二元组列表
    result = []
    for match in matches:
        _name = match[0].strip()
        _content = match[1].strip().replace('\n', '').strip()

        paren_level = 0
        new_content = ""
        for char in _content:
            if char == '[':
                paren_level += 1
                new_content += char
            elif char == ']':
                paren_level -= 1
                new_content += char
            elif char == '|' and paren_level == 0:
                continue
            else:
                new_content += char
        result.append( (_name, new_content))

    return result

def parser_yield( yield_clause, result):
    # 处理带括号的函数调用并提取属性名，如 properties(vertex).get_prob
    yield_parts = re.findall(r'properties\(\w+\)\.(\w+)', yield_clause)
    flag = 0
    for part in yield_parts:
        # 提取属性名（例如 properties(vertex).get_prob 提取为 get_prob）
        if part != '':
            if isinstance(result["object"], dict):
                result['object'][part] = "待查询"  # 将属性名作为键，值为 "待查询"
            else:
                result[ "other_yield" ].append( f"{part}:待查询")
            flag = 1
    
    # 处理普通的属性名
    simple_properties = re.findall(r'(\w+\.\w+)', yield_clause)
    for prop in simple_properties:
        if isinstance(result["object"], dict):
            result['object'][prop.split('.')[-1]] = "待查询"  # 只保留属性名部分
        else:
            result[ "other_yield" ].append( f"{prop.split('.')[-1]}:待查询")
        
        flag = 1
    
    if "," in yield_clause:
        clauses = yield_clause.split(",")
    else:
        clauses = [yield_clause]
    for clau in clauses:
        if "." not in clau:
            result[ "other_yield" ].append( re.split(r'\s+AS\s+', clau, flags=re.IGNORECASE)[0].strip())
    return result

def parser_where(where_clause, result):
    # 提取属性名、操作符（>=, ==, <= 等）和属性值，支持单引号和双引号括起来的字符串值
    where_parts = re.findall(r'(\w+\.\w+)\s*(>=|<=|==|!=|>)\s*(\'[^\']+\'|\"[^\"]+\"|\s|\d+\.\d+|\d|\w+)', where_clause)
    
    for prop, operator, value in where_parts:
        value = value.strip("'\" ")
        if operator == "==":
            # 如果是==，直接加到属性值中
            if isinstance(result["object"], dict):
                result["object"][prop.split('.')[-1]] = value
            else:
                result["restrict"].append(f"{prop} {operator} {value}")
        else:
            # 否则加到 "restrict" 列表中
            result["restrict"].append(f"{prop} {operator} {value}")
    return result

def parse_lookup_query( query ):
    # 初始化一个空字典来存储提取的信息
    result = { 
        'tag_or_type': None,
        'object' : {},
        'restrict': [],
        "other_yield": [],
        "other_clause": [],
    }
    split_list = split_ngql( query )
    for item in split_list:
        clause, content = item[0], item[1]
        result['other_clause'].append( clause )
        if clause.lower() == 'lookup on':
            result["tag_or_type"] = content
        elif clause.lower() == 'where':
            result = parser_where(content, result)
        elif clause.lower() == 'yield':
            result = parser_yield( content, result)
        else:
            # raise Exception( f"LOOKUP ON句子中意外的子句 {clause, content}")
            continue
    return result

def split_on_first_quote(s):
    # 使用正则表达式匹配第一个出现的单引号或双引号的位置
    match = re.search(r"(['\"])", s)
    
    if match:
        # 找到第一个引号的位置
        quote_pos = match.start()
        # 将字符串按第一个引号分为两部分
        return s[:quote_pos], s[quote_pos:]
    else:
        # 如果没有引号，返回原字符串和空字符串
        return s, ""
    
def parse_fetch_query( query ):    
    result = {
        "target" : "",
        "tag_or_type": [],
        "object" : [],
        'restrict': [],
        "other_yield": [],
        "other_clause": [],
    }
    splited = split_ngql( query )
    for clause in splited:
        clause_name = clause[0]
        fetch_obj = clause[1]
        result['other_clause'].append( clause_name )
        if clause_name.upper() == 'FETCH PROP ON':
            first_half, second_half = split_on_first_quote( fetch_obj )
            if "-" in second_half:
                result ["target"] = "edge"
            else:
                result ["target"] = "vertex"
            for type_ in first_half.split(" "):
                if  type_.strip() != "":
                    result ["tag_or_type"].append(  type_.strip() )
            for type_ in second_half.split(","):
                type_ = type_.strip()
                if  type_ != "":
                    if "->" in type_:
                        result ["object"].append(  {
                            "start_node": type_.split("->")[0].strip("\"' "),
                            "end_node": type_.split("->")[1].strip("\"' ")
                        } )
                    elif "<-" in type_:
                        result ["object"].append(  {
                            "start_node": type_.split("<-")[1].strip("\"' "),
                            "end_node": type_.split("<-")[0].strip("\"' ")
                        } )
                    else:
                        result ["object"].append(type_.strip("\"' "))
        elif clause_name.lower() == 'yield':
            result = parser_yield( fetch_obj, result)
        else:
            # raise Exception( f"LOOKUP ON句子中意外的子句 {clause, content}")
            continue
        
    return result

def parse_path_ngql(query):
    # 使用正则表达式提取 FROM, TO, OVER 以及 UPTO 后的内容
    from_match = re.search(r'FROM\s+"([^"]+)"(?:, "([^"]+)")?', query)
    to_match = re.search(r'TO\s+"([^"]+)"(?:, "([^"]+)")?', query)
    over_match = re.search(r'OVER\s+([^\s]+(?:,\s*[^\s]+)*)', query)
    upto_match = re.search(r'UPTO\s+\d+\s+STEPS', query)

    # 初始化返回的列表
    from_list = []
    to_list = []
    over_list = []
    upto_list = []

    # 提取 FROM 部分的元素
    if from_match:
        from_list = [from_match.group(1), from_match.group(2)] if from_match.group(2) else [from_match.group(1)]
    
    # 提取 TO 部分的元素
    if to_match:
        to_list = [to_match.group(1), to_match.group(2)] if to_match.group(2) else [to_match.group(1)]
    
    # 提取 OVER 部分的元素
    if over_match:
        over_list = over_match.group(1).split(", ")

    # 提取 UPTO 相关的内容
    if upto_match:
        upto_list.append(upto_match.group(0))  # 将整个 'UPTO 5 STEPS' 加入列表

    return from_list, to_list, over_list, upto_list

def parse_find_query( query ): 
    result = {
        "target" : "path",
        "tag_or_type": [],
        "object" : [],
        'restrict': [],
        "other_yield": [],
        "other_clause": [],
    }
    splited = split_ngql( query )
    for clause in splited:
        clause_name = clause[0]
        content = clause[1]
        result['other_clause'].append( clause_name )
        if clause_name.upper() == 'FIND':
            if not content.lower().strip().startswith( "path"):
                result["restrict"] = content.lower().split("path ")[0].strip()
            from_list, to_list, over_list, upto_list = parse_path_ngql( content )
            result["object"] .append(  {
                "start_node": from_list,
                "end_node": to_list,
                "edge": over_list,
                "range": upto_list
            } )
        elif clause_name.lower() == 'yield':
            result = parser_yield( content, result)
        else:
            # raise Exception( f"LOOKUP ON句子中意外的子句 {clause, content}")
            continue
    return result

def extract_edges_v2(subgraph_query):
    # 定义边方向关键字
    edge_keywords = ["OVER", "BOTH", "IN", "OUT"]
    
    # 构造正则模式，用于找到关键字的位置
    pattern = r'\b(OVER|BOTH|IN|OUT)\b'
    
    # 查找所有关键字的匹配及其位置
    matches = list(re.finditer(pattern, subgraph_query, flags=re.IGNORECASE))
    
    # 如果没有关键字，直接返回空字典
    if not matches:
        return {}
    
    # 初始化结果字典
    edge_dict = {}
    
    # 遍历匹配的关键字，提取每个关键字后的部分
    for i, match in enumerate(matches):
        # 当前关键字
        keyword = match.group(1).upper()  # 转为大写确保统一
        
        # 获取当前关键字后的内容
        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(subgraph_query)
        content = subgraph_query[start_pos:end_pos].strip()
        
        # 分割边名，去除多余空格
        if content:
            edge_list = [edge.strip() for edge in content.split(',') if edge.strip()]
            edge_dict[keyword] = edge_list
    
    # 移除空关键字项
    edge_dict = {key: value for key, value in edge_dict.items() if value}
    
    return edge_dict

def parse_subgraph_ngql(query):
    # 初始化结果列表
    with_prop_list = []
    steps_list = []
    from_nodes_list = []
    relation_list = []

    # 匹配 WITH PROP
    if 'WITH PROP' in query.upper():  # 大小写不敏感
        with_prop_list.append('WITH PROP')

    # 匹配 x steps
    steps_match = re.search(r'(\d+)\s+steps', query, re.IGNORECASE)
    if steps_match:
        steps_list.append(f"{steps_match.group(1)} steps")

    # 提取 FROM 后的所有节点
    objects = []
    # 用于存储边名，按 OVER、IN、OUT、BOTH 分类
    edge_dict = {}
    
    # 提取 From 后的对象名，匹配单引号或双引号包含的内容
    objects_pattern = r'["\'](.*?)["\']'
    objects = re.findall(objects_pattern, query)
    
    edge_dict = extract_edges_v2(query)

    return with_prop_list, steps_list, objects, edge_dict

def parse_subgraph_query( query ):
    result = {
        "target" : "path",
        "tag_or_type": [],
        "object" : {},
        'restrict': [],
        "other_yield": [],
        "other_clause": [],
    }
    splited = split_ngql( query )
    for clause in splited:
        clause_name = clause[0]
        content = clause[1]
        result['other_clause'].append( clause_name )
        if clause_name.upper() == 'GET SUBGRAPH':
            with_prop_list, steps_list, from_nodes_list, relation_list = parse_subgraph_ngql(content)
            result['restrict'].extend( with_prop_list )
            result['restrict'].extend( steps_list )
            result['object']["start_node"] = from_nodes_list
            result['object']["edge"] = relation_list
        elif clause_name.lower() == 'yield':
                result = parser_yield( content, result)
        else:
            # raise Exception( f"LOOKUP ON句子中意外的子句 {clause, content}")
            continue
    return result

def parse_go_ngql(query):
    # 初始化结果列表
    with_prop_list = []
    steps_list = []

    # 匹配 x steps
    steps_pattern = r'(\d+)(?:\s+to\s+(\d+))?\s+steps'
    steps_match = re.search(steps_pattern, query, re.IGNORECASE)
    if steps_match:
        if steps_match.group(2):  # 匹配到范围
            steps = (int(steps_match.group(1)), int(steps_match.group(2)))
            steps_list.append(f"{steps[0]} to {steps[1]} steps")
        else:  # 只匹配到单一数字
            steps = int(steps_match.group(1))
            steps_list.append(f"{steps} steps")
    
    # 检查并提取 REVERSELY 或 BIDIRECT
    direction_flags = []
    direction_pattern = r'\b(REVERSELY|BIDIRECT)\b'
    for match in re.findall(direction_pattern, query, flags=re.IGNORECASE):
        direction_flags.append(match.upper())
    # 从查询中移除 REVERSELY 和 BIDIRECT
    query = re.sub(direction_pattern, '', query, flags=re.IGNORECASE)

    # 提取 FROM 后的所有节点
    objects = []
    # 用于存储边名，按 OVER、IN、OUT、BOTH 分类
    edge_dict = defaultdict(list)
    
    # 提取 From 后的对象名，匹配单引号或双引号包含的内容
    objects_pattern = r'["\'](.*?)["\']'
    objects = re.findall(objects_pattern, query)
    
    # 提取边名部分，大小写不敏感匹配关键词 OVER、IN、OUT、BOTH
    edges_pattern = r'\b(OVER|IN|OUT|BOTH)\s+([\w\s,]*\*?)\s+(?=\bOVER|\bIN|\bOUT|\bBOTH|$|)'
    for match in re.findall(edges_pattern, query.strip(), flags=re.IGNORECASE):
        direction, edges = match
        if '*' in edges:
            # 如果匹配到 *，表示所有边
            edge_dict[direction.upper()].append('*')
        else:
            # 分割边名（支持逗号和空格分隔），并清理空格
            edge_list = [edge.strip() for edge in edges.split(',') if edge.strip()]
            edge_dict[direction.upper()].extend(edge_list)

    return direction_flags, steps_list, objects, dict(edge_dict)

def parse_go_query( query ):
    result = {
        "target" : "path",
        "tag_or_type": [],
        "object" : {},
        'restrict': [],
        "other_yield": [],
        "other_clause": [],
    }
    splited = split_ngql( query )
    for clause in splited:
        clause_name = clause[0]
        content = clause[1]
        result['other_clause'].append( clause_name )
        if clause_name.upper() == 'GO':
            direction_flags, steps_list, objects, edge_dict = parse_go_ngql( content )
            result[ "restrict" ].extend( direction_flags )
            result[ "restrict" ].extend( steps_list )
            result[ "object" ]["start_node"] = objects
            result[ "object" ]["edge"] = edge_dict
        elif clause_name.lower() == 'yield':
            result = parser_yield( content, result)
        else:
            # raise Exception( f"LOOKUP ON句子中意外的子句 {clause, content}")
            continue
    return result

def parse_write_query( query ):
    result = {
        "target" : "path",
        "tag_or_type": [],
        "object" : {},
        'restrict': [],
        "other_yield": [],
        "other_clause": [],
    }
    result["target"] = "write"
    return result

def parse_mixed_to_standard( query ):
    temp_result = {
        "query_pattern": "mixed",       # [ "node_or_edge", "relation_or_path", "sub_graph", "modify_db", "other"],        # multi_nodes包含单跳、多条关系，路径，遍历等
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
    splited = split_ngql( query )
    for clause in splited:
        clause_name = clause[0]
        content = clause[1]
        # 子句提取
        if clause not in temp_result["clauses"]:
            temp_result["clauses"].append( clause_name.lower() )

        if clause_name.upper() == 'GO':
            direction_flags, steps_list, objects, edge_dict = parse_go_ngql( content )
            temp_result[ "restrict" ].extend( direction_flags )
            temp_result[ "restrict" ].extend( steps_list )
            temp_result[ "related_objects" ].append({
                "start_node": objects,
                "edge": edge_dict
            })
        elif clause_name.upper() == 'FETCH PROP ON':
            first_half, second_half = split_on_first_quote( content )
            temp = {
                "type": "edge" if "-" in second_half else "vertex",
                "label": []
            }
            for type_ in first_half.split(" "):
                if  type_.strip() != "":
                    temp["label"].append(  type_.strip() )
            for type_ in second_half.split(","):
                type_ = type_.strip()
                if  type_ != "":
                    if "->" in type_:
                        temp["start_node"]= type_.split("->")[0].strip("\"' "),
                        temp["end_node"] = type_.split("->")[1].strip("\"' ")
                    elif "<-" in type_:
                        temp["start_node"]= type_.split("<-")[1].strip("\"' "),
                        temp["end_node"] = type_.split("<-")[0].strip("\"' ")
                    else:
                        temp["properties"] = type_.strip("\"' ")
            temp_result["related_objects"].append( temp )
        elif clause_name.upper() == 'FIND':
            if not content.lower().strip().startswith( "path"):
                temp_result["restrict"].append( content.lower().split("path ")[0].strip() )
            from_list, to_list, over_list, upto_list = parse_path_ngql( content )
            temp_result["related_objects"].append({
                "start_node": from_list,
                "end_node": to_list,
                "edge": over_list,
                "range": upto_list
            } )
        elif clause_name.upper() == 'LOOKUP ON':
            temp_result["related_objects"].append( {
                "label": content
            })
        elif clause_name.lower() == 'yield':
            temp_result["restrict"].append( content )
        else:
            continue
    return temp_result
