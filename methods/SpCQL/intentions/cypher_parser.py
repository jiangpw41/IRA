from wayne_utils import load_data, save_data
import re
from collections import OrderedDict
import ast
import os
from tqdm import tqdm

# cypher子句与关键字字典
cypher_clauses = {
    "MATCH": "用于在图中查找模式。	MATCH (n:Person)-[:FRIEND]->(m)。包含节点、边、路径三类组成的模式，以及用逗号分隔的独立模式", 
    "OPTIONAL MATCH": "类似 MATCH，但允许模式不匹配，返回 NULL。	OPTIONAL MATCH (n)-[:KNOWS]->(m)", 
    "WHERE": "为模式或结果添加过滤条件。	MATCH (n) WHERE n.age > 30 RETURN n", 
    "RETURN": "指定查询结果的输出。	RETURN n.name, n.age", 
    "WITH": "管道式传递中间结果，可用于聚合、过滤、或重命名。	WITH n.name AS name MATCH (m:City)", 
    "UNWIND": "将列表展开为行。	UNWIND [1, 2, 3] AS num RETURN num", 
    "CREATE": "创建节点、关系或子图。	CREATE (n:Person {name: 'Alice'})", 
    "MERGE": "查找或创建节点或关系。	MERGE (n:Person {name: 'Alice'})", 
    "SET": "更新节点或关系的属性或标签。	SET n.age = 30, n:Adult", 
    "DELETE": "删除节点、关系或子图。	MATCH (n) DELETE n", 
    "REMOVE": "移除节点或关系的标签或属性。	MATCH (n) REMOVE n.age", 
    "FOREACH": "针对列表中的每个元素执行一段写操作。	`FOREACH (x IN range(1,10)", 
    "CALL": "调用存储过程或自定义函数。	CALL dbms.procedures()", 
    "LOAD CSV": "导入 CSV 文件中的数据。	LOAD CSV FROM 'file:///data.csv' AS row", 
    "START": "基于图数据库索引查询，主要用于旧版。	START n=node(1) RETURN n", 
    "ORDER BY": "指定查询结果的排序顺序。	RETURN n ORDER BY n.name DESC", 
    "SKIP": "跳过指定数量的行。	RETURN n SKIP 10", 
    "LIMIT": "限制返回的结果行数。	RETURN n LIMIT 5", 
    "UNION": "合并两个查询的结果集（去重）。	MATCH (a:Person) RETURN a.name UNION ...", 
    "UNION ALL": "合并两个查询的结果集（不去重）。	MATCH (a:Person) RETURN a.name UNION ALL", 
}

cypher_keywords = {
    # 操作符关键字
    "AS": "为表达式或变量赋别名。示例：RETURN n.name AS playerName",
    "DISTINCT": "去重。示例：RETURN DISTINCT n.name",
    "CASE WHEN": "条件语句。示例：RETURN CASE WHEN n.age > 30 THEN 'Adult' ELSE 'Young' END",
    "EXISTS": "检查是否存在某个模式或属性。示例：WHERE EXISTS (n.name)",
    # 模式相关关键字
    "ALL": "在条件中表示“所有”。示例：WHERE ALL(x IN [1, 2, 3] WHERE x > 0)",
    "ANY": "在条件中表示“任意”。示例：WHERE ANY(x IN [1, 2, 3] WHERE x > 0)",
    "NONE": "在条件中表示“没有”。示例：WHERE NONE(x IN [1, 2, 3] WHERE x > 0)",
    "SINGLE": "在条件中表示“只有一个”。示例：WHERE SINGLE(x IN [1, 2, 3] WHERE x > 2)",
    # 列表和路径相关关键字
    "ALLSHORTESTPATHS": "查找所有最短路径。示例：MATCH p=ALLSHORTESTPATHS((a)-[*]->(b)) RETURN p",
    "SHORTESTPATH": "查找两个节点之间的一条最短路径。",
    "PATHS": "通常结合 MATCH 语句，表示模式中捕获的路径。",
    "RELATIONSHIPS": "获取路径中的所有关系。示例：UNWIND RELATIONSHIPS(path) AS rel",
    "NODES": "获取路径中的所有节点。示例：RETURN NODES(path)",
    "PROPERTIES": "获取节点或关系的所有属性。示例：RETURN PROPERTIES(n)"
}

node_labels = [ "entity" ]
node_properties = [ "name", "location", "time" ]
edge_labels = [ "relationship", "describe", "tag", "ambiguity" ]
node_properties = [ "name"]

########################################### 处理match子句 ###########################################
# 从字符串中抽取字典
def extract_dict_from_str( properties_str ):
    item_list = properties_str.split( ",")
    ret_dict ={}
    for item in item_list:
        key, value = item.split(":")[0].strip(), item.split(":")[1].strip()
        ret_dict[key] = value
    return ret_dict

# 解析圆括号
def parse_circle_content(content):
    """
    解析圆括号内的内容
    """
    result = {
        "type": "circle",
        "variable": None,
        "labels": [],
        "properties": {}
    }
    # 提取变量部分
    variable_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)', content)
    if variable_match:
        result["variable"] = variable_match.group(1)
        content = content[len(variable_match.group(0)):].strip()
    
    # 提取标签部分
    label_match = re.findall(r':([a-zA-Z_][a-zA-Z0-9_]*)', content)
    if label_match:
        result["labels"] = label_match
    
    # 提取属性部分
    properties_match = re.search(r'\{(.+?)\}', content)
    if properties_match:
        properties_str = properties_match.group(1)
        try:
            result["properties"] = extract_dict_from_str( properties_str )
        except:
            result["properties"] = {}
    
    return result

# 解析圆方括号
def parse_square_content(content):
    """
    解析方括号内的内容
    """
    result = {
        "type": "square",
        "variable": None,
        "relationship_type": None,
        "properties": {},
        "length_range": None
    }
    # 提取变量部分
    variable_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)', content)
    if variable_match:
        result["variable"] = variable_match.group(1)
        content = content[len(variable_match.group(0)):].strip()
    
    # 提取关系类型部分
    relationship_match = re.search(r':([a-zA-Z_][a-zA-Z0-9_]*)', content)
    if relationship_match:
        result["relationship_type"] = relationship_match.group(1)
    
    # 提取长度范围部分
    length_range_match = re.search(r'\*\s*([0-9]*\.\.[0-9]*|[0-9]+)', content)
    if length_range_match:
        result["length_range"] = length_range_match.group(1).strip()
    
    # 提取属性部分
    properties_match = re.search(r'\{(.+?)\}', content)
    if properties_match:
        properties_str = properties_match.group(1)
        try:
            result["properties"] = extract_dict_from_str( properties_str )
        except:
            result["properties"] = {}
    
    return result

# 解析所有括号
def extract_elements_with_skeleton(cypher_query):
    """
    提取Cypher语句中圆括号和方括号内的元素，并保留语句骨架。
    
    Args:
        cypher_query (str): Cypher语句。
        
    Returns:
        dict: 包含两部分：
              1. "elements" (list): 每个括号内容解析为字典（圆括号或方括号）。
              2. "skeleton" (str): 原语句中除括号内容外的骨架。
    """
    # 定义正则模式
    circle_pattern = r'\(([^()]+)\)'  # 圆括号模式
    square_pattern = r'\[([^()]+)\]'  # 方括号模式

    # 提取括号内容
    elements = []
    skeleton = cypher_query  # 初始骨架为原语句

    # 提取并替换圆括号
    for match in re.finditer(circle_pattern, cypher_query):
        elements.append(parse_circle_content(match.group(1)))
        skeleton = skeleton.replace(match.group(0), "()", 1)  # 替换为占位符

    # 提取并替换方括号
    for match in re.finditer(square_pattern, cypher_query):
        elements.append(parse_square_content(match.group(1)))
        skeleton = skeleton.replace(match.group(0), "[]", 1)  # 替换为占位符

    return {"elements": elements, "skeleton": skeleton.strip()}

# 判断变量名是否是纯字母
def judge_alpha( var ):
    if not var.isalpha():
        return f"不合法的变量名"
    else:
        return True

# 判断字符串中是否存在一个 "=" 号，且该 "=" 号不在任何括号内。
def has_unenclosed_equals(input_string):
    """
    :param input_string: 要检查的字符串
    :return: 如果存在符合条件的 "=" 返回 True，否则返回 False
    """
    new_input_string = input_string.replace("（", "(").replace("）", ")")
    stack = []  # 用于追踪括号的栈
    for i, char in enumerate(new_input_string):
        if char in "([{":
            stack.append(char)  # 开括号入栈
        elif char in ")]}":
            if stack and ((stack[-1] == "(" and char == ")") or
                          (stack[-1] == "[" and char == "]") or
                          (stack[-1] == "{" and char == "}")):
                stack.pop()  # 匹配的闭括号出栈
            else:
                # print(f"字符串中的括号不匹配{new_input_string}")
                return False
        elif char == "=":
            if not stack:  # 如果栈为空，说明当前 "=" 不在括号内
                return True
    return False  # 遍历结束，没有符合条件的 "="

# 将match子句按逗号分割
def split_outside_brackets(s):
    stack = []  # 用于记录括号的栈
    result = []
    current = []
    bracket_pairs = {')': '(', ']': '[', '}': '{'}
    
    for i, char in enumerate(s):
        if char in '([{':
            stack.append(char)
            current.append(char)  # 当前段落继续收集字符
        elif char in ')]}':
            if not stack or stack[-1] != bracket_pairs[char]:
                # 如果发现括号不匹配，返回原始字符串
                return [s]
            stack.pop()
            current.append(char)
        elif char == ',' and not stack:
            # 如果是逗号且在括号外
            result.append(''.join(current).strip())
            current = []
        else:
            current.append(char)

    # 如果括号不匹配，返回原始字符串
    if stack:
        return [s]
    
    # 添加最后一段
    if current:
        result.append(''.join(current).strip())
    
    return result

# 处理match子句
def process_match_clause( match_clause_original ):

    match_clause_list = split_outside_brackets( match_clause_original )
    path_dict_lists = []
    match_skeleton_list = []                     # 骨架字符串
    variables = []                                    # 变量列表
    for match_clause in match_clause_list:
        match_skeleton = ""
        if has_unenclosed_equals(match_clause):     # 有路径定义
            match_skeleton += "="
            path_var, path_func = match_clause.split("=")[0].strip(), match_clause.split("=")[1].strip()
            if not path_var.isalpha():
                # raise Exception( f"变量名不合法：{path_var}，完整子句为{match_clause}")
                return match_clause, [], []
            if path_var not in variables:
                variables.append( path_var )
        else:
            path_func = match_clause
        ret = extract_elements_with_skeleton(path_func)    # 提取核心部分
        match_skeleton = match_skeleton + ret['skeleton']
        path_dict_list = ret['elements']

        for dicts in path_dict_list:
            if dicts['variable'] != None and dicts['variable'] not in variables:
                variables.append( dicts['variable'] )
            dicts['variable'] = None
        for dicts in path_dict_list:
            if dicts not in path_dict_lists:
                path_dict_lists.append( dicts )
        match_skeleton_list.append( match_skeleton )

    return ",".join(match_skeleton_list), variables, path_dict_lists

###################################### 处理所有子句 #########################################
# 按照子句进行分割
def split_cypher_clauses(query: str) -> dict:
    clause_pattern = re.compile(
        r"\b(" + r"|".join(re.escape(clause.lower()) for clause in cypher_clauses) + r")\b"
    )
    matches = list(clause_pattern.finditer(query))
    if not matches:
        return {}
    result = OrderedDict({})
    for i, match in enumerate(matches):
        clause = match.group(1)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(query)
        result[clause] = query[start:end].strip()
    """获取所有有as的子句
    for i in range( len(gold_query_list)):
        if " as " in gold_query_list[i].lower():
            print(i)
    37
    41
    73
    76
    88
    92
    """

    """获取所有match子句
    parse_list = []
    for i in range(len(gold_query_list)):
        parse_list.append( split_cypher_clauses( gold_query_list[i].lower() ) )
    parse_list
    all_matches = []
    for i in range(len(parse_list)):
        all_matches.append( parse_list[i]["match"] )
    all_matches
    """

    return result

# 从as关键字后提取变量名
def extract_variables_from_as( clause_dict ):
    # 查找 AS 关键字后的变量名（可能是多个）
    variables = []
    for key in clause_dict.keys():
        if key != "match" and " as " in clause_dict[key]:
            matches = re.findall(r'\bas\b\s+([\w,\s]+)', clause_dict[key], re.IGNORECASE)
            for match in matches:
                # 分割多个变量（以逗号为分隔符）
                variables.extend([var.strip() for var in match.split(',')])
    return variables

# 从单个子句中移除变量名
def remove_variables_from_string(input_string, variables):
    """
    从字符串中移除指定的变量名称，支持以下形式：
    1. 变量作为独立词出现，例如：`return p`
    2. 变量作为属性的前缀，例如：`p.name`
    3. 变量作为函数的参数，例如：`count(p)`, `count( p )`, `count( p)`
    
    :param input_string: 待处理的字符串
    :param variables: 要移除的变量名称列表
    :return: 移除变量后的字符串
    """
    # 构建正则表达式，匹配变量及其可能的上下文
    for var in variables:
        input_string = re.sub(
            rf'(?<!\w){re.escape(var)}(?!\w)(?=\s*[\.\(\),]*\s*)',  # 匹配变量，确保独立
            '',  # 替换为空
            input_string
        )
    
    # 清理多余空格和符号
    input_string = re.sub(r'\s+', ' ', input_string).strip()  # 清理多余空格
    input_string = re.sub(r'\(\s*\)', '()', input_string)     # 清理空括号
    input_string = re.sub(r'\[\s*\]', '[]', input_string)     # 清理空方括号
    return input_string

# 从所有子句中移除变量名
def remove_variables_from_clause( clause_dict, variables ):
    for key in clause_dict.keys():
        if key != "match":
            clause_dict[key] = remove_variables_from_string( clause_dict[key], variables)
    return clause_dict


##################################### 解析与比较 #######################################
# 解析单个cypher
def process_cypher( clause_dict ):
    if "match" in clause_dict:
        match_clause = clause_dict["match"]
        match_skeleton, variables, match_path_dict_list = process_match_clause( match_clause )
        clause_dict["match"] = {
            "skeleton" : match_skeleton,
            "dict_list": match_path_dict_list
        }
    else:
        variables = []
    variables.extend( extract_variables_from_as( clause_dict ) )
    clause_dict = remove_variables_from_clause( clause_dict, variables )
    return clause_dict, variables

# 解析全部cypher
def batch_process_cypher( query_list):
    ret_list = []
    for i in range( len( query_list )):
        query = query_list[i]
        clause_dict = split_cypher_clauses( query.lower() )
        clause_dict, variables  = process_cypher( clause_dict )
        ret_list.append( (clause_dict, variables) )
    return ret_list