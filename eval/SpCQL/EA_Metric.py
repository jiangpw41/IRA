def dict2set( ans_single, index):
    "将所有结果的值放到集合里"
    results_set = set()
    for dicts in ans_single:
        if not isinstance( dicts, dict):
            raise Exception( f"不是字典 {index} : {ans_single}")
        for key in dicts.keys():
            value = dicts[key]
            if not isinstance( value, str):
                if isinstance( value, int ):
                    value = str(value)
                    results_set.add( value )
                elif isinstance( value, list ):
                    for sub_value in value:
                        if not isinstance( sub_value, dict):
                            results_set.add( sub_value )
                        else:
                            for key in sub_value.keys():
                                results_set.add( sub_value[key] )
                elif isinstance( value, dict ):
                    for key in value:
                        results_set.add( value[key] )
                elif value == None:
                    continue
                else:
                    raise Exception( f"不是字符串 {index} : {ans_single}")
            else:
                results_set.add( value )
    return results_set

# 匹配式，还有N3的相似度式
def Neo4j_ExecutionAccuracy_Match( predict_list: list[str], label_list: list[str], SA_list: list[str]):
    if sum(SA_list) == 0:
        return 0 , 0, 0, SA_list, SA_list
    EA_list = []
    EEA_list = []
    for index in range( len(predict_list)):
        gold_ans_single = label_list[index]
        predict_ans_single = predict_list[index]
        # 如果是字符串结果，则是错误、终止返回
        if not SA_list[index]:
            EA_list.append( False )
            EEA_list.append( False )
        else:
            if isinstance( predict_ans_single , str):
                predict_results_set = set()
            else:
                
                predict_results_set = dict2set( predict_ans_single, index )
            gold_results_set = dict2set( gold_ans_single, index )
            if gold_results_set == predict_results_set:
                EA_list.append( True )
                EEA_list.append( True )
            else:
                EA_list.append( False )
                if gold_results_set.issubset( predict_results_set ):
                    EEA_list.append( True )
                else:
                    EEA_list.append( False )
    EA = sum(EA_list) *100 / len(EA_list)
    EEA = sum(EEA_list) *100 / len(EEA_list)
    IEA = sum(EA_list) *100 / sum(SA_list)
    return EA, EEA, IEA, EA_list, EEA_list
