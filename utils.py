from wayne_utils import load_data, save_data
import os
from config import _ROOT_PATH

def split_merge( split_query ):
    split_dict = load_data( "data/N3/split_dict.json", "json")
    order_dict = {}
    total_len = 0
    
    for key in ['disease', 'potter', 'nba']:
        dict_index_list = split_dict['index'][key]
        query_list = split_query[key]
        total_len += len(query_list)
        for i in range(len(query_list)):
            index = dict_index_list[i]
            if index not in order_dict:
                order_dict[index] = (query_list[i], key)
            else:
                raise Exception( f"Index重复:{index}")
    if total_len != len(order_dict):
        raise Exception( f"长度不一致:{total_len, len(order_dict)}")
    ret_list = []
    space_list = []
    for i in range( total_len ):
        query, key = order_dict[i ]
        space_list.append( key)
        ret_list.append( query)
    return ret_list, space_list

def Check_result( metric, method, dataset, sub_method = None, overwrite = False):
    if dataset == "SpCQL":
        result_path = os.path.join( _ROOT_PATH, "results/SpCQL_eval_results.json")
    elif dataset == "N3":
        result_path = os.path.join( _ROOT_PATH, "results/N3_eval_results.json")
    else:
        raise Exception(f"不存在的数据集{dataset}")
    results_dict = load_data( result_path, "json")

    
    # 如果方法不存在，说明是第一次运行
    if method not in results_dict:
        value = None
    # 如果方法存在
    else:
        # 检查子方法
        if sub_method != None:
            # 如果子方法不存在，说明是第一次运行
            if sub_method not in results_dict[method]:
                value = None
            # 如果子方法存在
            else:
                # 检查该指标是否存在
                if metric not in results_dict[method][sub_method]:
                    value = None
                else:
                    value = results_dict[method][sub_method][metric]
        else:
            # 如果指标不存在，说明是第一次运行
            if metric not in results_dict[method]:
                value = None
            else:
                value = results_dict[method][sub_method][metric]
    if value != None:
        if overwrite:
            print(f"已经存在记录{method}-{sub_method}-{metric} = {value}，但允许重写。")
            return True
        else:
            print(f"已经存在记录{method}-{sub_method}-{metric} = {value}，不允许重写。")
            return False
    else:
        print(f"不存在记录{method}-{sub_method}-{metric}，允许重写。")
        return True

def Record_result( metric, value, method, dataset, sub_method = None):
    if dataset == "SpCQL":
        result_path = os.path.join( _ROOT_PATH, "results/SpCQL_eval_results.json")
    elif dataset == "N3":
        result_path = os.path.join( _ROOT_PATH, "results/N3_eval_results.json")
    else:
        raise Exception(f"不存在的数据集{dataset}")
    results_dict = load_data( result_path, "json")
    # 如果当前结果字典中不存在主方法，则添加
    if method not in results_dict:
        results_dict[method] = {}
    # 如果主方法中不存在子方法
    if sub_method != None and sub_method not in results_dict[method]:
        results_dict[method][sub_method] = {}
        
    metric_dict = results_dict[method] if sub_method==None else results_dict[method][sub_method]
    if metric not in metric_dict:
        print( f"新的记录：{method}{sub_method}的{metric} = {value}")
        metric_dict[ metric ] = value
    else:
        print( f"已有记录：{method}{sub_method}的{metric} = {metric_dict[ metric ]}，新值为{value}")
        metric_dict[ metric ] = value
    if sub_method==None:
        results_dict[method] = metric_dict
    else:
        results_dict[method][sub_method] = metric_dict

    save_data(results_dict, result_path )

def format_float(value):
    # 保留两位小数，如果结果是 100.0 或 0.0，保留一位小数
    formatted_value = round(value, 2)
    if formatted_value == 100.0 or formatted_value == 0.0:
        return f"{formatted_value:.1f}"
    return f"{formatted_value:.2f}"