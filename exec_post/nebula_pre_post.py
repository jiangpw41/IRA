from tqdm import tqdm

def R3Post_old( predict_result, gold_result ):
    result_list = []
    # Check if the query execution succeeded
    if predict_result == None:
        ret_predict_result = "语法错误"
    elif predict_result.is_succeeded() == False:
        ret_predict_result = "语法错误"
    else:
        n = predict_result.row_size()
        for i in range(n):
            result_list.append(str(predict_result.row_values(i)))
        if len(result_list) == 0 and len(gold_result) != 0:
            ret_predict_result = "语法错误"
        elif len(result_list) != 0 and result_list[0] == "[__NULL__]" and len(gold_result) != 0:
            ret_predict_result= "语法错误"
        else:
            ret_predict_result = result_list
    return ret_predict_result

def R3Post( predict_result ):
    # Check if the query execution succeeded
    if predict_result == None:
        ret_predict_result = "其他错误"
    elif predict_result.is_succeeded() == False:
        if predict_result.error_code() == -1004:
            ret_predict_result = "语法错误"
        else:
            ret_predict_result = "其他错误"
    else:
        ret_predict_result = predict_result
    return ret_predict_result

def R3Post_Batch( predict_result_list ):
    processed_list = []
    for i in tqdm( range( len(predict_result_list) ), desc = "R3 postprocessing..." ):
        processed_list.append( R3Post( predict_result_list[i]) )
    return processed_list

def R3_pre_process( input_str_list ):
    ret_list = []
    for i in range(len(input_str_list)):
        ret_list.append(  input_str_list[i].strip(" \"'"))
    return ret_list

if __name__ == "__main__":
    from wayne_utils import load_data

    total_list = []
    gold_list = []
    gold_result = load_data( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher_data_process/R3_db_construction/inter_results_dict/0_gold_result_list.json", "json")
    gpt_result = load_data( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher_data_process/R3_db_construction/inter_results_dict/execute_1_R3_GPT-4.pickle", "pickle")
    for key in gpt_result.keys():
        gold_list.extend( gold_result[key] )
        total_list.extend( gpt_result[key] )
    processed_list = R3Post_Batch( total_list, gold_list )
    print( len(processed_list) )