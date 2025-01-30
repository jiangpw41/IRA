#######################################For gold results#####################################
def comma_split( input_str, index):
    "合规性检查"
    if input_str[0] == "[": 
        if input_str[-1] != "]":
            raise Exception( f"Index {index}: 方括号不匹配 {input_str}")
        input_str = input_str[1:-1].strip()
    if "," not in input_str:
        if input_str.strip() in [ "", '""']:
            return []
        return [input_str]
    "括号匹配"
    ret_list = []
    bracket_stack = []
    left_index = 0
    for i in range(len(input_str)):
        cur_str = input_str[i]
        if cur_str == "[" or cur_str == "(" or cur_str == "{":
            bracket_stack.append( cur_str )
        elif cur_str == "]" or cur_str == ")" or cur_str == "}":
            last = bracket_stack.pop()
            if (cur_str == "]" and last != "[") or (cur_str == ")" and last != "(") or (cur_str == "}" and last != "{"):
                raise Exception( f"Index {index}: 括号不匹配 {cur_str, last}；String{input_str}")
        elif cur_str == "," and len(bracket_stack) == 0:
            # 获得以逗号为分隔的子部分
            ret_list.append( input_str[ left_index: i].strip() )
            left_index = i+1
    ret_list.append( input_str[ left_index:].strip() )
    return ret_list

def two_level_split( task, index):
    first_level = comma_split( task, index)
    new_first_level = []
    for item in first_level:
        if item[0] == "[" and item[-1] == "]":
            second_level = comma_split( item, index)
            new_first_level.append( second_level )
        elif item[0] != "[" and item[-1] != "]":
            new_first_level.append( item )
        else:
            raise Exception( f"Index {index}: 括号不匹配；String{item}")
    return new_first_level

def gold_result_post( gold_result, index ):
    task_list = eval( str(gold_result))
    new_task_list = []
    for task in task_list:
        two_level = two_level_split( task, index)
        new_task_list.append( two_level )
    return new_task_list

def post_gold_result( gold_result_list):
    gold_post_list = []
    for index in range( len(gold_result_list) ):
        # index = 0
        gold_result  = gold_result_list[index]
        new_task_list = gold_result_post( gold_result, index)
        gold_post_list.append( new_task_list )
    return gold_post_list

#######################################For predict results#####################################
import nebula3
# for nba execute
def execute_result_post( execute_result, index):
    if isinstance( execute_result, nebula3.data.ResultSet.ResultSet):
        """如果是标准结果，则继续处理"""
        if execute_result.is_succeeded():
            if execute_result.is_empty():
                return []
            else:
                ret = []
                """是成功执行、非空返回"""
                flag = 0
                try:
                    result_list = list(execute_result)
                except:
                    flag = 1
                    result_list = []
                    lens = execute_result.row_size()
                    for i in range(lens):
                        result_list.extend( execute_result.row_values(i))
                # 这里的for循环构成了第二层子列表的数量
                for result in result_list:
                    sub_ret_list = []
                    if not isinstance( result, nebula3.data.DataObject.Record) and flag == 0:
                        raise Exception( f"Index {index}: 结果列表中元素非Record {result}")
                    else:
                        """是Record类型列表中的元素"""
                        if flag == 0:
                            record_values = result.values()
                        else:
                            record_values = result_list
                        for value in record_values:
                            
                            """遍历values列表中的wrap"""
                            if isinstance( value, nebula3.data.DataObject.ValueWrapper):
                                if value.is_vertex() or value.is_path() or value.is_edge() or value.is_string()  or value.is_int() or value.is_double():
                                    "最简单的形式，单个答案"
                                    if not (value.is_string() and value.as_string() == "nan"):
                                        sub_ret_list.append( str(value) )
                                elif value.is_list():
                                    record_list = []
                                    "稍稍复杂，列表多个"
                                    value_sub_list = value.as_list()
                                    for sub_value in value_sub_list:
                                        if sub_value.is_vertex() or sub_value.is_path() or sub_value.is_edge() or sub_value.is_string():
                                            """但凡是节点、边、路径三者之一，就作为最小单元字符串加入"""
                                            record_list.append( str(sub_value) )
                                        else:
                                            raise Exception( f"Index {index}: 不可识别的sub_value类型：{type(sub_value), sub_value}")
                                    sub_ret_list.append( record_list )
                                elif value.is_map():
                                    sub_ret_list.append( str(value) )
                                elif value.is_null() or value.is_empty():
                                    continue
                                else:
                                    raise Exception( f"Index {index}: 不可识别的value类型：{type(value), value}")

                            else:
                                raise Exception(f"Index {index}: Record values列表中不是ValueWrapper {value}")
                    
                    ret.append( sub_ret_list )
                return ret
        else:
            # print( f"Index : {index}； 执行错误，error message = {execute_result.error_code()} " )
            if execute_result.error_code() == -1004:
                return "语法错误"
            else:
                return []
    else:
        # print( f"Index : {index}； {execute_result}" )
        return []

def post_execute_result( predict_result_list):
    execute_post_list = []
    for index in range(len(predict_result_list)):
        ret_list = execute_result_post( predict_result_list[index], index )
        execute_post_list.append( ret_list )
    return execute_post_list


if __name__ == "__main__":
    from wayne_utils import load_data

    total_list = []
    gold_list = []
    gold_result = load_data( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher_data_process/N3_db_construction/inter_results_dict/0_gold_result_list.json", "json")
    gpt_result = load_data( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher_data_process/N3_db_construction/inter_results_dict/execute_1_n3_GPT-4.pickle", "pickle")
    for key in gpt_result.keys():
        gold_list.extend( gold_result[key] )
        total_list.extend( gpt_result[key] )
    gold_processed_list = post_gold_result( gold_list )
    predict_processed_list = post_execute_result( total_list )
    #print( len(processed_list) )