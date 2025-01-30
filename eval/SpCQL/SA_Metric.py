from tqdm import tqdm

def Neo4j_SyntaxAccuracy( predict_list: list[str]):
    "Syntax_Accuracy: 语法准确性，通过图形数据库评估生成的GQL是否可以在没有语法错误的情况下执行"
    ret_list = []
    error_count = 0
    for i in range( len(predict_list) ):
        resp = predict_list[i]
        if isinstance( resp, str):
            error_count += 1
            if resp == "语法错误":
                ret_list.append( False )
            else:
                ret_list.append( True )
        else:
            ret_list.append( True )
        
    # 计算正确比例
    ER = error_count*100 / len(ret_list)
    SA = sum(ret_list)*100 / len(ret_list)
    return SA, ER, ret_list

if __name__ == "_main__":
    print("")