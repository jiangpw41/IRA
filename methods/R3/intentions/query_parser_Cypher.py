import re
from query_parser_nGQL import split_ngql

def split_by_comma_outside_parentheses(s):
    result = []
    current = []
    stack = []
    
    for char in s:
        if char == ',' and not stack:  # 检查是否在括号外
            # 当前部分加入结果列表
            result.append(''.join(current).strip())
            current = []  # 清空当前部分
        else:
            current.append(char)
            if char in '([{':  # 遇到左括号，入栈
                stack.append(char)
            elif char in ')]}':  # 遇到右括号，出栈
                if stack and ((char == ')' and stack[-1] == '(') or 
                              (char == ']' and stack[-1] == '[') or 
                              (char == '}' and stack[-1] == '{')):
                    stack.pop()
    
    # 把最后一部分加入结果
    if current:
        result.append(''.join(current).strip())
    
    return result

def match_pattern_path_spliter(s):
    # 检查是否有括号外的等号
    if '=' in s:
        restrict = None
        # 以等号分割为两部分
        parts = s.split('=', 1)
        left_part = parts[0].strip()
        right_part = parts[1].strip()
        # 检查右部分是否完全包裹在一个圆括号内
        for function in ["shortestpath", "allshortestpaths"]:
            if function in right_part.lower():
                restrict = function
                right_part = re.sub(function, "", right_part, flags=re.IGNORECASE)
        if right_part.replace(" ", "").startswith("(("):
            right_part = right_part[1:-1].strip()
        return left_part, restrict, right_part
    else:
        return s.strip(), None, None

def match_pattern_spliter(query):
    components = []                     # 用于存储最终结果    
    current = []                        # 用于缓存当前正在构建的组件 
    in_parentheses = False              # 记录当前是否在括号内，以及括号类型
    in_square_brackets = False
    stack = []                          # 遍历字符的堆栈（考虑嵌套括号的情况）
    for char in query:                                              # 遍历字符串
        if char == '(':                                             # 如果遇到左括号，进入括号内的逻辑
            if not in_parentheses and not in_square_brackets:
                if current:                                         # 把括号外积压的箭头等部分加入结果列表
                    components.append(''.join(current).strip())
                    current = []
                in_parentheses = True
            stack.append(char)
            current.append(char)                                    # 当前左括号字符加入组件中
        elif char == '[':
            if not in_parentheses and not in_square_brackets:
                # 把括号外的部分加入结果
                if current:
                    components.append(''.join(current).strip())
                    current = []
                in_square_brackets = True
            stack.append(char)
            current.append(char)
        # 如果遇到右括号，退出括号内的逻辑
        elif char == ')':
            if stack and stack[-1] == '(':
                stack.pop()  # 配对成功，弹出堆栈
            current.append(char)
            if not stack:  # 如果堆栈为空，说明当前括号结束
                components.append(''.join(current))
                current = []
                in_parentheses = False
        elif char == ']':
            if stack and stack[-1] == '[':
                stack.pop()  # 配对成功，弹出堆栈
            current.append(char)
            if not stack:  # 如果堆栈为空，说明当前括号结束
                components.append(''.join(current))
                current = []
                in_square_brackets = False
        # 处理逗号（子句分割）
        elif char == ',' and not in_parentheses and not in_square_brackets:
            if current:
                components.append(''.join(current).strip())
                current = []
        else:
            current.append(char)  # 普通字符加入当前组件

    # 把最后残留的部分加入结果
    if current:
        components.append(''.join(current).strip())

    return components

def extract_cypher_node(node_str):
    # 定义默认的节点信息字典
    node_info = { "type": "node", "variable_name": None, "label": [], "properties": None}
    
    # 匹配节点字符串，捕获变量名、标签和属性
    match = re.match(
        r'\(\s*'                  # 匹配起始的圆括号和可选空格
        r'(\w+)?\s*'              # 可选的变量名（首个单词）
        r'(?:\s*:\s*([\w:]+))?'   # 可选的标签部分（冒号后，可以有多个用:分隔）
        r'(?:\s*\{\s*([^}]*)\s*\})?'  # 可选的属性部分（花括号内内容）
        r'\s*\)',                 # 匹配结束的圆括号和可选空格
        node_str
    )
    
    if match:
        var_name, labels, props = match.groups()
        
        # 提取变量名
        if var_name:
            node_info["variable_name"] = var_name.strip(" '\"")
        
        # 提取标签，按冒号分割为列表
        if labels:
            node_info["label"] = [label.strip() for label in labels.split(':') if label.strip()]
        
        # 提取属性
        if props:
            properties = {}
            # 将键值对字符串解析为字典
            for pair in props.split(','):
                key_value = pair.split(':', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    properties[key.strip()] = value.strip(" '\"")
            node_info["properties"] = properties
    
    return node_info

def extract_cypher_relationship(rel_str):
    # 定义默认的关系信息字典
    rel_info = {
        "type": "edge",
        "variable_name": None,       # 变量名
        "label": [],       # 标签
        "length": None,    # 关系长度
        "properties": None # 属性
    }
    # 匹配关系字符串，捕获变量名、标签、长度和属性
    match = re.match(
        r'\[\s*'                      # 匹配起始的方括号和可选空格
        r'(\w+)?\s*'                  # 可选的变量名
        r'(?:\s*:\s*([\w|]+))?'       # 可选的标签部分，整体捕获为一个字符串
        r'(?:\s*\*\s*([\w.\d]+))?'    # 可选的关系长度（以*开头）
        r'(?:\s*\{\s*([^}]*)\s*\})?'  # 可选的属性（花括号内内容）
        r'\s*\]',                     # 匹配结束的方括号和可选空格
        rel_str
    )
    if match:
        var_name, labels, length, props = match.group(1), match.group(2), match.group(3), match.group(4)
        # 提取变量名
        if var_name:
            rel_info["variable_name"] = var_name.strip()
        
        # 提取标签，按冒号分割为列表
        if labels:
            rel_info["label"] = [label.strip() for label in labels.split('|') if label.strip()]
        
        # 提取关系长度
        if length:
            rel_info["length"] = length.strip()
        
        # 提取属性
        if props:
            properties = {}
            for pair in props.split(','):
                key_value = pair.split(':', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    properties[key.strip()] = value.strip()
            rel_info["properties"] = properties
    
    return rel_info

def transform_to_obj( core ):
    obj_list = []
    for i in range( len(core) ):
        comp = core[i].strip()
        # 如果是节点
        if comp.startswith("(") and comp.endswith(")"):
            obj = extract_cypher_node( comp )
            obj_list.append( obj )
        elif comp.startswith("[") and comp.endswith("]"):
            obj = extract_cypher_relationship( comp )
            obj_list.append( obj )
        elif comp == "--":
            # 处理省略的关系
            obj_list.append( "-" )
            obj_list.append( extract_cypher_relationship( "[]" ) )
            obj_list.append( "-" )
        elif comp == "<--":
            # 处理省略的关系
            obj_list.append( "<-" )
            obj_list.append( extract_cypher_relationship( "[]" ) )
            obj_list.append( "-" )
        elif comp == "-->":
            # 处理省略的关系
            obj_list.append( "-" )
            obj_list.append( extract_cypher_relationship( "[]" ) )
            obj_list.append( "->" )
        else:
            obj_list.append( comp )
    return obj_list

def parse_obj_list( obj_list ):
    node_list = []
    edge_list = []
    for i in range( len(obj_list) ):
        obj = obj_list[i]
        # 如果是节点对象
        if isinstance( obj, dict) and obj["type"] == "node":
            if edge_list != []:
                for key in ["end_node", "start_node"]:
                    if edge_list[-1][key] == None:
                        edge_list[-1][key] = obj
                        break
            node_list.append( obj )
        # 如果是边对象
        elif isinstance( obj, dict) and obj["type"] == "edge":
            if len(node_list) == 0:
                return []
            try:
                left_line, right_line = obj_list[i-1], obj_list[i+1]
            except:
                return []
            
            if left_line == "-" and right_line == "-":
                # 无向关系
                obj["start_node"] = node_list[-1]
                node_list.pop()
                obj["end_node"] = None
                obj["direction"] = False
                edge_list.append( obj )
            elif left_line == "<-":
                # 向左关系
                obj["end_node"] = node_list[-1]
                node_list.pop()
                obj["start_node"] = None
                obj["direction"] = True
                edge_list.append( obj )
            elif right_line == "->":
                # 向右边关系
                obj["start_node"] = node_list[-1]
                node_list.pop()
                obj["end_node"] = None
                obj["direction"] = True
                edge_list.append( obj )
            else:
                return []
                # raise Exception( f"不合法的边关系：{obj_list} || {obj}")
            
        else:
            continue
    if len(edge_list) > 0:
        return edge_list # merge_multi_edge( edge_list )
    else:
        return node_list

def match_clause_parser( query ):
    
    query_sublist = split_by_comma_outside_parentheses( query )
    result_list = []
    for subquery in query_sublist:
        #
        left_part, restrict, right_part = match_pattern_path_spliter( subquery )
        
        # 如果是路径变量
        if right_part != None:
            #print( "路径变量")
            path_var, path_str = left_part, right_part
            splited_pattern = match_pattern_spliter( path_str )
            obj_list = transform_to_obj( splited_pattern )
            
            parsed_obj_list = parse_obj_list( obj_list )
            if len(parsed_obj_list) == 1:
                parsed_obj_list[0]["type"] = "path"
                parsed_obj_list[0]["restrict"] = restrict
            '''else:
                raise Exception( f"变量对象不合法：{parsed_obj_list}")'''
        # 如果不是路径变量
        else:
            #print( "非路径变量")
            path_var = None
            
            splited_pattern = match_pattern_spliter( left_part )
            obj_list = transform_to_obj( splited_pattern )
            parsed_obj_list = parse_obj_list( obj_list )
            
        result_list.extend( parsed_obj_list )
    return result_list

def parse_where_clause(where_clause):
    # 初始化结果
    result = {
        "property_restrict": [],  # 存放常规属性约束的字典
        "other_restrict": []  # 存放函数形式约束的字符串
    }

    # 根据逗号分割子句，strip 去掉首尾空格
    conditions = [cond.strip() for cond in where_clause.split(",")]

    # 正则匹配
    property_pattern = re.compile(r"(\w+)\.(\w+)\.(\w+)\s*==\s*(['\"].+?['\"])")  # 属性匹配
    function_pattern = re.compile(r"(\w+)\((\w+)\)\s*==\s*(['\"].+?['\"]|\d+)")  # 函数匹配

    for cond in conditions:
        # 匹配常规属性约束
        prop_match = property_pattern.match(cond)
        if prop_match:
            variable, label, prop, value = prop_match.groups()
            result["property_restrict"].append({
                "variable": variable,
                "label": label,
                "property": prop,
                "value": value.strip("'\"")  # 去掉引号
            })
            continue

        # 匹配函数形式约束
        func_match = function_pattern.match(cond)
        if func_match:
            func_name, variable, value = func_match.groups()
            result["other_restrict"].append(f"{func_name}({variable}) == {value}")
            continue

        # 未匹配的条件直接放入 other_restrict
        result["other_restrict"].append(cond)

    return result

def add_property_to_dict( restrict_dict, obj):
    _var_name = restrict_dict['variable']
    _label = restrict_dict['label']
    _property = restrict_dict['property']
    _value = restrict_dict['value']
    if obj["type"] == "node":
        if _var_name == obj["variable_name"] and _label in obj["label"]:
            if obj['properties'] == None:
                obj['properties'] = {}
            obj['properties'][_property] = _value
    elif obj["type"] == "edge":
        add_property_to_dict( restrict_dict, obj["start_node"])
        add_property_to_dict( restrict_dict, obj["end_node"])
                
def add_property( property_restrict, match_result_list ):
    for restrict in property_restrict:
        # 遍历match中的对象
        for obj in match_result_list:
            add_property_to_dict( restrict, obj)

def parse_return_clause(return_clause):
    """
    解析Cypher RETURN子句。
    
    Args:
        return_clause (str): RETURN子句的字符串内容。
        
    Returns:
        dict: 包含字段和函数的解析结果。
    """
    result = {
        "properties": [],  # 存储类似 n1.college.name 的字段
        "distinct" : False,
        "return_object": []  # 存储函数调用，如 count(n1)
    }
    if "distinct" in return_clause.lower():
        result["distinct"] = True

    # 根据逗号分割字段
    return_parts = [part.strip() for part in return_clause.split(",")]
    
    for part in return_parts:
        # 提取类似 n1.college.name 格式
        field_match = re.match(r'(\w+)\.(\w+)\.(\w+)', part)
        if field_match:
            var, label, prop = field_match.groups()
            result["properties"].append({
                "variable": var,
                "label": label,
                "property": prop,
                "value": "待查询"
            })
        else:
            if " as " in part.lower():
                split_pattern = re.compile(re.escape(" as "), flags=re.IGNORECASE)
                part = split_pattern.split(part)[0].strip()
            result["return_object"].append(part)
    
    return result

def parse_match_query( query ):
    result = {
        "query_pattern": None,       # [ "node_or_edge", "relation_or_path", "sub_graph", "modify_db", "other"],        # multi_nodes包含单跳、多条关系，路径，遍历等
        "recommend_keywords": "match",
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
        result["clauses"].append( clause_name.lower() )
        content = clause[1]
        if clause_name.upper() == 'MATCH':
            match_result_list = match_clause_parser( content )
            result["related_objects"].extend( match_result_list )
        elif clause_name.upper() == 'WHERE':
            where_result_dict = parse_where_clause(content)
            result['restrict'].extend( where_result_dict['other_restrict'])
            add_property( where_result_dict['property_restrict'], result["related_objects"] )
        elif clause_name.upper() == 'RETURN':
            ret_format = parse_return_clause(content)
            add_property( ret_format['properties'], result["related_objects"] )
            del ret_format['properties']
            result["return_format"].update(ret_format )
        elif clause_name.upper() == 'ORDER BY':
            result['order by'] = content
        elif clause_name.upper() == 'LIMIT':
            result['limit'] = content
        elif clause_name.upper() == 'SKIP':
            result['skip'] = content
        else:
            # raise Exception(f"不合法的Match子句 {clause} || {query} ")
            continue
        
    if len(result["related_objects"]) == 1 and result["related_objects"][0]["type"] in ["node", "edge"]:
        result["query_pattern"] = "node_or_edge"
    else:
        result["query_pattern"] = "relation_or_path"
    return result


if __name__ == "__main__":
    from wayne_utils import load_data, save_data
    from type_stat import nGQL_classify, get_intention
    import os
    os.chdir( "/home/jiangpeiwen2/jiangpeiwen2/NL2GQL/methods/MyMethod/N3/intentions")
    unique_list = load_data( "all_unique_list.json", "json")    # 1300
    class_dict = nGQL_classify( unique_list )
    match_list = class_dict["MATCH"]
    intentions = get_intention( match_list, parse_match_query)
    intentions[0]