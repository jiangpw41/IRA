import bert_score
from tqdm import tqdm

empty_words = [ '__NULL__', "", '__EMPTY__', '"__NULL__"', '"NULL"', '"null"', 'BAD_TYPE', "nan", '""', '"nan"']

def flatten_list( _result_list ):
    ret = []
    for _item in _result_list:
        if isinstance( _item, list):
            ret.extend( flatten_list(_item) )
        else:
            if _item not in empty_words:
                ret.append( _item)
    return ret

def key_value_str( input_str ):
    sub_kvs = input_str.split(",")
    ret_dict = {}
    for sub_kv in sub_kvs:
        if ":" in sub_kv:
            key = sub_kv.split( ":")[0].strip()
            value = sub_kv.split( ":")[1].strip()
            if value not in empty_words:
                ret_dict[key] = value
    return ret_dict

def split_property_dict( item ):
    "返回被挖空的字符串和一个字典列表"
    dict_list = []
    rest_string = ""

    left_huakuo_index, right_huakuo_index= [], []
    for i in range(len(item)):
        cur_str = item[i]
        if cur_str == "{":
            left_huakuo_index.append( i )
        elif cur_str == "}":
            right_huakuo_index.append( i )
    if len(left_huakuo_index) != len(right_huakuo_index):
        raise Exception( f"花括号长度不一致：{len(left_huakuo_index), len(right_huakuo_index)}; \n String {item}")
    edge_left = 0
    dict_s = []
    for i in range(len(left_huakuo_index)):
        left_index, right_index = left_huakuo_index[i], right_huakuo_index[i]
        edge_right = left_index
        rest_string += item[ edge_left: edge_right+1]
        dict_s.append( item[ left_index+1: right_index])
        edge_left = right_index
    rest_string += item[ edge_left:]

    for dict_str in dict_s:
        dict_list.append( key_value_str( dict_str ) )
    return dict_list, rest_string

def split_string_dict( _flatten_list ):
    dict_ret, string_ret = [], []
    for i in range( len(_flatten_list) ):
        _string = _flatten_list[i]
        if "{" in _string and "{}" not in _string and "," in _string:
            _dict_list_temp, _rest_string = split_property_dict( _string )
            dict_ret.extend( _dict_list_temp )
            string_ret.append( _rest_string )
        else:
            string_ret.append( _string )
    return dict_ret, string_ret

def dict_involve( gold_dict_list, predict_dict_list):
    # gold是否被预测结果包含
    flag = 1
    for sub_dict in gold_dict_list:
        if sub_dict not in predict_dict_list:
            flag = 0
            break
    return flag

def Inner_EA(gold_str_list, predict_str_list, gold_dict_list, predict_dict_list ):
    # 如果不完全相等，但是gold的结果是predict的子集，即预测结果包含gold，则+1
    if set( gold_str_list ).issubset( set( predict_str_list ) ):
        return dict_involve( gold_dict_list, predict_dict_list)
    return False

def ExecuteAccurary(_gold_result, _predict_result ):
    flatten_gold_result, flatten_predict_result= flatten_list( _gold_result ), flatten_list( _predict_result )
    gold_dict_list, gold_str_list = split_string_dict( flatten_gold_result )                    # 获取字符串部分
    predict_dict_list, predict_str_list = split_string_dict( flatten_predict_result )           # 获取字典部分
    
    # 字符串部分列表是否完全相等
    if set( gold_str_list ) == set( predict_str_list ):
        # 字典部分列表是否等长
        if len( gold_dict_list ) == len(predict_dict_list):
            EA = dict_involve( gold_dict_list, predict_dict_list)
        else:
            EA = False
    else:
        EA = False

    if not EA:
        EEA = Inner_EA(gold_str_list, predict_str_list, gold_dict_list, predict_dict_list )
    else:
        EEA = True
    
    return EA, EEA


def My_EA_Batch( execute_post_lit, gold_post_lit , SA_list):
    if sum( SA_list ) == 0:
        return 0, 0, SA_list, SA_list
    if len( execute_post_lit) != len( gold_post_lit ):
        raise Exception( f"长度不一致{len( execute_post_lit), len( gold_post_lit )}")
    EA_list, EEA_list, IEA_list = [], [], []
    for i in tqdm( range( len(gold_post_lit) ), desc = f"After evaluating"):
        _gold_result, _predict_result = gold_post_lit[i], execute_post_lit[i]
        if SA_list[i] == True:
            single_EA, single_EEA = ExecuteAccurary(_gold_result, _predict_result )
            EA_list.append( single_EA  )
            EEA_list.append( single_EEA  )
            IEA_list.append( single_EA )
        else:
            EA_list.append( False  )
            EEA_list.append( False  )
    EA = sum(EA_list) * 100 / len(EA_list)
    IEA = sum(IEA_list) * 100 / len(IEA_list)
    EEA = sum(EEA_list) * 100 / len(EEA_list)
    return EA, IEA, EEA, EA_list, EEA_list
    

if __name__ == "__main__":
    from wayne_utils import load_data
    from My_postprocess import post_gold_result, post_execute_result
    from Syntax_Accuracy import SA_Batch
    total_list = []
    gold_list = []
    gold_result = load_data( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher_data_process/N3_db_construction/inter_results_dict/0_gold_result_list.json", "json")
    gpt_result = load_data( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher_data_process/N3_db_construction/inter_results_dict/execute_1_n3_GPT-4.pickle", "pickle")
    for key in gpt_result.keys():
        gold_list.extend( gold_result[key] )
        total_list.extend( gpt_result[key] )
    gold_processed_list = post_gold_result( gold_list )
    predict_processed_list = post_execute_result( total_list )
    SA, SA_list = SA_Batch( predict_processed_list )
    print( SA )

    EA, IEA, EA_list, IEA_list = My_EA_Batch( predict_processed_list, gold_processed_list , SA_list)
    print( EA, IEA )