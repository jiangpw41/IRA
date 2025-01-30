import os

os.chdir( "/home/jiangpeiwen2/jiangpeiwen2/NL2GQL/methods/MyMethod/R3/intentions" )
from type_stat import nGQL_classify
from query_parser_standard import get_single_intention, parse_intention

def judge_clauses(intention_label,intention_predict  ):
    # 如果子句列表不一样，直接返回0
    label_clause, predict_clause = set(), set()
    for item in intention_label['clauses']:
        label_clause.add( item.lower().strip() )
    for item in intention_predict['clauses']:
        predict_clause.add( item.lower().strip() )
    return label_clause == predict_clause

def judge_return_format(intention_label, intention_predict):
    label_ret_format, predict_ret_format = intention_label['return_format'], intention_predict['return_format']
    if label_ret_format['distinct'] != predict_ret_format['distinct']:
        return False
    else:
        # limit
        if label_ret_format['limit'] != predict_ret_format['limit']:
            return False
        
        # order by
        if label_ret_format['order by'] != None and predict_ret_format['order by'] != None:
            if label_ret_format['order by'].strip().lower().replace(" ", "") != predict_ret_format['order by'].strip().lower().replace(" ", ""):
                # order by都是字符串但不相等，直接返回False
                return False
        elif label_ret_format['order by'] != predict_ret_format['order by']:
                return False
        
        # skip
        if label_ret_format['skip'] != None and predict_ret_format['skip'] != None:
            if label_ret_format['skip'].strip().lower().replace(" ", "") != predict_ret_format['skip'].strip().lower().replace(" ", ""):
                # order by都是字符串但不相等，直接返回False
                return False
        elif label_ret_format['skip'] != predict_ret_format['skip']:
                return False
        
        # 'return_object'是否一致
        label_return_list, predict_return_list = set(), set()
        if label_ret_format['return_object'] == predict_ret_format['return_object']:
            pass
        else:
            if label_ret_format['return_object']:
                for item in label_ret_format['return_object']:
                    label_return_list.add( item.split("(")[0].lower().strip() )
            if predict_ret_format['return_object']:
                for item in predict_ret_format['return_object']:
                    predict_return_list.add( item.split("(")[0].lower().strip() )
        return label_return_list == predict_return_list

def judge_restrict(intention_label,intention_predict  ):
    # 如果子句列表不一样，直接返回0
    label_len = len(intention_label["restrict"])
    predict_len = len(intention_predict["restrict"])
    if (label_len == 0 and predict_len == 0) or (label_len > 0 and predict_len > 0):
        return True
    else:
        return False


def get_set_from_list( single_list:list ):
    key_set, value_set = set(), set()
    for item in single_list:
        if isinstance( item, dict):
            temp_key, temp_value = get_set_from_dict( item )
            key_set.update( temp_key )
            value_set.update( temp_value )
        elif isinstance( item, list):
            temp_key, temp_value = get_set_from_list( item )
            key_set.update( temp_key )
            value_set.update( temp_value )
        else:
            value_set.add( item )
    return key_set, value_set

def get_set_from_dict( single_obj:dict ):
    key_set, value_set = set(), set()
    for key in single_obj:
        key_set.add( key )
        value = single_obj[key]
        if isinstance( value, dict):
            temp_key, temp_value = get_set_from_dict( value )
            key_set.update( temp_key )
            value_set.update( temp_value )
        elif isinstance( value, list):
            temp_key, temp_value = get_set_from_list( value )
            key_set.update( temp_key )
            value_set.update( temp_value )
        else:
            value_set.add( value )
    return key_set, value_set

def judge_objects(intention_label,intention_predict  ):
    # 如果子句列表不一样，直接返回0
    labels = intention_label["related_objects"]
    predicts = intention_predict["related_objects"]
    if len(labels) != len(predicts):
        return False
    else:
        label_key_set, preidct_key_set = set(), set()
        label_value_set, preidct_value_set = set(), set()
        for i in range(len(labels)):
            key_set, value_set = get_set_from_dict( labels[i] )
            label_key_set.update( key_set )
            label_value_set.update( value_set )
            
            key_set, value_set = get_set_from_dict( predicts[i] )
            preidct_key_set.update( key_set )
            preidct_value_set.update( value_set )
           
        return label_key_set == preidct_key_set and label_value_set == preidct_value_set





def Single_EM_R3( predict_query, label_query):
    if predict_query.lower().replace( " ", "").replace( "\n", "") == label_query.lower().replace( " ", "").replace( "\n", ""):
        # 如果完全一致，直接返回1
        return 1
    else:
        # 如果不完全一致，先解析为意图字典
        predict_class_dict = nGQL_classify( [predict_query] )
        label_class_dict = nGQL_classify( [label_query] )

        keyword_predict, intention_predict = get_single_intention( parse_intention(predict_class_dict )[0] )
        keyword_label, intention_label = get_single_intention( parse_intention(label_class_dict  )[0])
        flag = keyword_predict == keyword_label and \
                judge_clauses(intention_label, intention_predict) and \
                judge_return_format(intention_label, intention_predict) and \
                judge_restrict(intention_label,intention_predict  ) and \
                judge_objects(intention_label,intention_predict  )
        return flag





def ExactSetMatch( gold_query_list, predict_query_list ):
    if len(gold_query_list) != len(predict_query_list):
        raise Exception( f"长度不一致{ len(gold_query_list), len(predict_query_list)}")
    "完全一致"
    EM_list = []
    for i in range( len(gold_query_list)):
        EM_list.append( Single_EM_R3( predict_query_list[i], gold_query_list[i]) )
    EM = sum(EM_list)*100 / len(EM_list)
    return EM, EM_list



