from cypher_parser import split_cypher_clauses, process_cypher
from copy import deepcopy
import re


def divide_cypher_type( tests ):
    paths = []              # 370       556
    single_left = []        # 409       1386
    single_right = []       # 399       2226
    two_orient = []         # 572       1993
    no_orient = []          # 202       761
    single_node = []        # 20        79
    multi_match = []        # 1
    others = []             # 33       0
    not_comma_others = []   # 0         0
    for i in range(len(tests)):
        cypher = tests[i]['cypher']
        clause_dict = split_cypher_clauses( cypher.lower() )
        clause_dict_new, variables  = process_cypher( deepcopy(clause_dict) )
        # 是否是单节点
        if cypher.lower().count("match") > 1:
            multi_match.append( (i, cypher) )             # 多个match的复杂情况
        elif "-" not in cypher:
            single_node.append( (i, cypher) )            # 没有路径箭头的单节点
        else:
            # 简单查询，match没有逗号
            if clause_dict["match"].count( ",") == 0:           # match子句没有逗号分隔，是一般的节点、关系和路径
                if ")--(" in cypher.replace(" ", ""):           # 无方向的两个节点关系：or "-[]-" in cypher.replace(" ", ""):
                    no_orient.append( (i, cypher) )
                elif "*" in clause_dict["match"]:               # 路径（长度范围）
                    paths.append( (i, cypher) )
                elif clause_dict["match"].count("<-") == 1 and clause_dict["match"].count("->") == 1:
                        two_orient.append( (i, cypher) )
                elif clause_dict["match"].count("->") == 1:
                    single_right.append( (i, cypher) )
                elif clause_dict["match"].count("<-") == 1:
                    single_left.append( (i, cypher) )

                
                else:
                    not_comma_others.append( (i, cypher) )   
            # 有逗号
            else:
                # 只有一个
                if clause_dict["match"].count( ",") == 1:
                    if clause_dict["match"].count("<-") == 1 and clause_dict["match"].count("->") == 1:
                        two_orient.append( (i, cypher) )
                    else:
                        others.append( (i, cypher) )
                else:
                    multi_match.append( (i, cypher) )
    return paths, single_left, single_right, two_orient, no_orient, single_node, multi_match, others, not_comma_others

def extract_names_single(cypher_query):
    # 匹配所有 name:'值' 的模式
    pattern = r"name:'([^']+)'"
    
    # 找到所有匹配项并返回值列表
    names = re.findall(pattern, cypher_query)
    return names

# 抽取左右方向简单
def get_left_right( single_left_right, left=True):
    intents_list = []
    for i in range(len(single_left_right)):
        original_index = single_left_right[i][0]
        temp = extract_names_single(single_left_right[i][1])
        '''if len(temp) != 2:
            print(f"错误{i} {single_left_right[i]}")'''
        if not left and len(temp)>1 and len(temp) % 2 != 0:
            print(f"错误{i} {single_left_right[i]}")
            
        if left:
            inten = {
                "name": "待查询",
            }
            if len( temp ) == 2:
                inten[temp[1]]= temp[0]
            elif len( temp ) == 1:
                inten["未知属性"]= temp[0]
            else:
                print(f"长度错误{i} {single_left_right[i]}")
        else:
            inten = {
                "name": "待查询",
            }
            if len( temp ) == 2:
                inten["name"] = temp[0]
                inten[ temp[1] ] = "待查询"
            elif len( temp ) == 1:
                inten["name"] = temp[0]
                inten["未知属性"]= "待查询"
            else:
                print(f"右单侧错误{i} {single_left_right[i]}")
        intents_list.append( (original_index, inten) )
    return intents_list

def extract_names_and_commas(cypher_query):
    # 匹配 name:'值' 或者逗号
    pattern = r"(name:'([^']+)'|,)"
    
    # 找到所有匹配项
    matches = re.finditer(pattern, cypher_query)
    
    # 按顺序提取值和逗号
    result = []
    for match in matches:
        if match.group(1) == ',':
            result.append(',')
        else:
            result.append(match.group(2))
    
    return result

# 获取双向
def get_two_orient( single_left_right, test=True):
    intents_list = []
    for i in range(len(single_left_right)):
        original_index = single_left_right[i][0]
        cypher = single_left_right[i][1].lower()
        clause_dict = split_cypher_clauses( cypher.lower() )
        temp = extract_names_and_commas(clause_dict["match"])
        lefts = []
        rights = []
        '''comma_c = 0
        for j in range(len(temp)):
            if temp[j] == ",":
                comma_c +=1
        if comma_c>1:
            print(f"错误{i} {single_left_right[i]} {temp}" )'''
        have_com = 0
        
        for j in range(len(temp)):
            if temp[j] != ",":
                lefts.append(temp[j])
            else:
                have_com = 1
                rights.extend( temp[j+1:])
                break
        
        if have_com:
            inten = {}
            if len(lefts) ==1:          # 左边只有属性值
                inten["未知属性"] = lefts[0]
            elif len(lefts) ==2:
                inten[ lefts[1] ] = lefts[0]
            else:
                print(f"左边长度错误{i} {single_left_right[i]} /// {temp}" )

            if len(rights) ==1:          # 右边边只有属性值
                inten[ rights[0] ] = "待查询"
            elif len(rights) ==2:
                inten[ rights[0] ] = rights[1]
                inten[ "name" ] = "待查询"
            elif '大学教师' in cypher:
                inten[ "name" ] = "待查询"
                inten[ lefts[1] ] = lefts[0]
                inten[ "未知属性" ] = '大学教师'
            else:
                if not test:
                    inten[ "name" ] = "待查询"
                else:
                    print(f"右边长度错误{i} {single_left_right[i]} /// {temp}" )
        else:
            inten = {}
            if len(lefts) == 2:
                if "<-[:Tag{name:'标签'}]->" not in cypher:
                    inten[ "name" ] = "待查询"
                    inten[ lefts[1] ] = lefts[0]
                elif "<--(" in cypher and "-->(" in cypher:
                    inten[ "name" ] = "待查询"
                    inten[ "未知属性" ] = lefts[0]
                    inten[ "未知属性1" ] = lefts[1]
                
                else:
                    inten[ "未知属性" ] = lefts[0]
                    inten[ "未知属性" ] = "待查询"
                # print(f"无逗号长度为2 {i} {single_left_right[i]} /// {temp}" )
            elif len(lefts) == 3:
                inten[ lefts[1] ] = lefts[0]
                inten[ lefts[2] ] = "待查询"
            elif len(lefts) == 4:
                inten[ "name" ] = "待查询"
                inten[ lefts[1] ] = lefts[0]
                inten[ lefts[2] ] = lefts[3]
                
            else:
                print(f"无逗号长度为{len(temp)} {i} {single_left_right[i]} /// {temp}" )
            '''else:
                if len(lefts) == 4:
                    inten[ "name" ] = "待查询"
                    inten[ lefts[1] ] = lefts[0]
                    inten[ lefts[2] ] = lefts[3]
                else:
                    print(f"无逗号长度为3——{i} {single_left_right[i]} /// {temp}" )'''

        intents_list.append( (original_index, inten) )
    return intents_list

# 获取无向
def get_no_orient( lists ):
    intents_list = []
    for i in range(len(lists)):
        original_index = lists[i][0]
        cypher = lists[i][1].lower()
        clause_dict = split_cypher_clauses( cypher.lower() )
        temp = extract_names_single(clause_dict["match"])
        if len(temp) == 1:
            intents_list.append( (original_index, {
                "name" : temp[0],
                "未知属性": "待查询"
            }) )
        else:
            print(f"错误{i} {lists[i]} {temp}")
    return intents_list

# 获取单节点
def get_single_node( single_node ):
    ret_list = []
    for i in range(len(single_node)):
        original_index = single_node[i][0]
        cypher = single_node[i][1]
        intens = {}
        match_clause = cypher.split("return")[0].strip()
        return_clause = cypher.split("return")[1].strip()
        if "name" in match_clause:
            temp = extract_names_single( match_clause)
            intens["name"] = temp[0]
            if ".location" in return_clause:
                intens["location"] = "待查询"
            elif ".time" in return_clause:
                intens["time"] = "待查询"
        elif "location:'" in match_clause:
            name_ = match_clause.split("location:'")[1].split("'})")[0].strip()
            intens["location"] = name_
            intens["name"] = "待查询"
        elif "time:'" in match_clause:
            name_ = match_clause.split("time:'")[1].split("'})")[0].strip()
            intens["time"] = name_
            intens["name"] = "待查询"
        else:
            print(f"错误{i} {single_node[i]}")
        
        ret_list.append( (original_index, intens ) )
    return ret_list

# 获取联合节点
def get_union_node( multi_match):
    intents_list = []
    for i in range(len(multi_match)):
        original_index = multi_match[i][0]
        cypher = multi_match[i][1].lower()
        match_parts = cypher.split("match")
        intens = {}
        for parts in match_parts:
            temp = extract_names_single(parts)
            if len(temp) == 2:
                if "name" not in intens:
                    intens["name"] = temp[0]
                intens[temp[1]] = "待查询"
            elif len(temp) == 1:
                intens[temp[0]] = "待查询"
            elif len(temp) == 0:
                continue
            elif len(temp) == 3:
                intens["name"] = temp[0]
                intens[temp[1]] = "待查询"
                intens[temp[2]] = "待查询"
            else:
                print(f"联合节点错误{i} {multi_match[i]} {temp}")
                break
        intents_list.append( (original_index, intens ) )
    return intents_list

# 获取其他节点
def get_other_node( others ):
    intents_list = []
    for i in range(len(others)):
        original_index = others[i][0]
        cypher = others[i][1].lower()
        first_part = cypher.split("\n")[0].strip()
        temp = extract_names_single(first_part)
        intens_1 = {
            "name": temp[0],
            "相关属性": temp[1]
        }
        intens_2 = {
            "相关属性": temp[1],
            "标签": "待查询"
        }
        intens = [intens_1, intens_2]
        intents_list.append( ( original_index, intens ) )
    return intents_list

def extract_path_range(input_str):
    # 正则表达式匹配路径长度范围
    pattern = r'\*\s*(\d+\.\.\d+|\.\.\d+|\d+\.\.|\d+|\.{2})?'
    match = re.search(pattern, input_str)
    if match:
        # 获取捕获的范围值
        range_part = match.group(1)
        return range_part if range_part else "没有长度约束"
    return "匹配失败"

# 获取路径
def get_path_node( paths ):
    intents_list = []
    for i in range(len(paths)):
        original_index = paths[i][0]
        cypher = paths[i][1].lower()
        clause_dict = split_cypher_clauses( cypher.lower() )
        matchs = clause_dict["match"]
        temp = extract_names_single( matchs )
        if "->" in matchs:
            dire = "right"
        elif "<-" in matchs:
            dire = "left" 
        else:
            dire = "None"
        if len(temp) == 1:
            intens = {
                "节点1":{
                    "name" : temp[0]
                },
                "节点2":{
                    "name" : "待查询"
                },
                "方向":dire,
                "路径长度": extract_path_range(matchs)
            }
        elif len(temp) == 2:
            intens = {
                "节点1":{
                    "name" : temp[0]
                },
                "节点2":{
                    "name" : temp[1]
                },
                "方向":dire,
                "路径长度": extract_path_range(matchs)
            }
        else:
            print(f"长度错误{i} {matchs} {temp}")
        intents_list.append( ( original_index, intens) )
    
    return intents_list


def get_not_comma( not_comma_others ):
    intents_list = []
    for i in range(len(not_comma_others)):
        original_index = not_comma_others[i][0]
        cypher = not_comma_others[i][1].lower()
        temp = extract_names_single(cypher)
        if "商都" in cypher:
            intens = {
                "name" : "待查询",
                temp[1]: temp[0]
            }
        else:
            intens = {}
        intents_list.append( (original_index, intens))
    return intents_list