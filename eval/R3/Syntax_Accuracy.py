
import nebula3
from tqdm import tqdm

      

def SA_Batch( exec_result_list ):
    if not isinstance( exec_result_list, list) or len( exec_result_list )==0:
        raise Exception( f"不合法的结果列表{ type(exec_result_list) }")
    SA_list = []
    Other_error = 0
    for i in tqdm( range( len(exec_result_list) ), desc="SA evaluating..." ):
        result = exec_result_list[i]
        if isinstance( result, str):
            if result == "语法错误":
                SA_list.append( False )
            else:
                SA_list.append( True )
                Other_error += 1
        else:
            SA_list.append( True )

    SA = sum( SA_list )*100 / len( SA_list )
    ER = Other_error *100  / len( SA_list )
    return SA, SA_list, ER

if __name__ == "__main__":
    
    print("aa" )