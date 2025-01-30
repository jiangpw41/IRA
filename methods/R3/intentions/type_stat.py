import re

def get_gql_results( input_string, tests ):
    for i in range(len(tests)):
        if tests[i]['content'] == input_string:
            return tests[i]['result']
    return ""
def get_gql_query( input_string, tests ):
    ret_list = []
    for i in range(len(tests)):
        if tests[i]['content'] == input_string:
            ret_list.append( tests[i]['prompt'] )
    return ret_list
def contains_pipe_outside_parentheses(query):
    depth_r, depth_s = 0, 0  # 括号嵌套深度
    for i, char in enumerate(query):
        if char == '(':
            depth_r += 1
        elif char == ')':
            depth_r -= 1
        elif char == '[':
            depth_s += 1
        elif char == ']':
            depth_s -= 1
        elif char == '|' and depth_r == 0 and depth_s == 0:  # 如果是管道符，且当前深度为 0
            return True
    return False
def count_unique_occurrences(substr, total, strict = True):
    if strict:
        # 在字符串B中查找A的所有匹配，要求A作为单独的部分，左右是空格或者没有字符
        pattern = r'(?<!\S)' + re.escape(substr) + r'(?!\S)'  # 通过前后是非字字符来确保A是独立的部分
        
        matches = re.findall(pattern, total, flags=re.IGNORECASE)
        return len(matches)
    else:
        return total.lower().count( substr.lower() )
def type_judge( query ):
    # 写操作识别
    number = count_unique_occurrences("INSERT", query)
    if number > 0:
        return ["INSERT"], number
    if count_unique_occurrences("CREATE", query)>0 or \
        count_unique_occurrences("UPSERT", query)>0 or \
        count_unique_occurrences("DROP", query)>0 or \
        count_unique_occurrences("DELETE", query)>0 or \
        count_unique_occurrences("SET", query)>0 or \
        count_unique_occurrences("ADD", query)>0 or \
        count_unique_occurrences("CLEAR", query)>0 or \
        count_unique_occurrences("REBUILD", query)>0 or \
        count_unique_occurrences("UPDATE", query)>0:
        return ["OTHER_WRITE"], 0
    # 读操作识别
    read_keys = [ "MATCH", "FETCH PROP ON", "LOOKUP ON", "FIND", "GET SUBGRAPH", "GO", "SHOW"]
    read_list = [0, 0, 0, 0, 0, 0, 0]
    for i, key in enumerate( read_keys ):
        number = count_unique_occurrences(key, query, False) if key == "MATCH" else count_unique_occurrences(key, query)
        read_list[i] = number
    if sum( read_list ) > 0:
        ret_key_list = []
        ret_key_number = 0
        for i in range( len(read_keys) ):
            if read_list[i] > 0:
                ret_key_list.append( read_keys[i])
                ret_key_number += 1
        return ret_key_list, ret_key_number
    else:
        if count_unique_occurrences("RETURN", query, False) > 0 or count_unique_occurrences("YIELD", query) > 0:
            return ["QUICK_RETURN"], 0
        else:
            return ["OTHER"], 0

def nGQL_classify( nGQL_list ):
    ret_dict = {
        # 涉及写
        "INSERT": [],                           # 37      0
        "OTHER_WRITE": [],                      # 117     0
        
        # 仅读
        "MATCH": [],                            # 543     347
        "FETCH PROP ON": [],                    # 69      12
        "LOOKUP ON": [],                        # 106     42
        "FIND":[],                              # 43      10
        "GET SUBGRAPH": [],                     # 34      16
        "GO": [],                               # 189     79
        "SHOW": [],                             # 23      0
        "MIXED": [],                            # 22      5
        "QUICK_RETURN": [],                     # 84:     0          Return 或 yield
        "OTHER": []                             # 33      0
    }
    for i in range( len(nGQL_list)):
        query = nGQL_list[i]
        lists, number = type_judge( query )
        if len(lists) > 1 or number>1:
            if query not in ret_dict[ "MIXED" ]:
                ret_dict[ "MIXED" ].append( query )
        elif len(lists) == 1 and number <= 1:
            key = lists[0]
            if query not in ret_dict[ key ]:
                ret_dict[key].append( query )
        else:
            raise Exception(f"不合法的长度{len(lists)} {lists, number}")
    
    return ret_dict


def pint_intention( index, part_list, intentions):
    print( f"nGQL：{part_list[index]}")
    print( f"intention:{intentions[index]}")

def get_intention( part_list, method):
    ret_list = []
    for i in range( len(part_list) ):
        ret_list.append( method(part_list[i]))
    return ret_list