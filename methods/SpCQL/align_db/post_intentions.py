import re
import ast

# 从第一部分提取
def extract_dict_from_one(input_str):
    """
    从字符串中提取字典部分并解析为 Python 字典。
    
    参数:
        input_str (str): 包含字典的字符串，例如 "对象: {'name': '乙夜[日本军优]', '职业': '待查询'},"
        
    返回:
        dict: 提取并解析后的字典。
    """
    # 使用正则匹配字典部分
    match = re.search(r"\{.*?\}", input_str)
    if match:
        dict_str = match.group(0)  # 提取匹配的字典字符串
        try:
            # 使用 ast.literal_eval 将字符串安全地转换为字典
            return ast.literal_eval(dict_str)
        except (ValueError, SyntaxError) as e:
            print(f"解析字典失败: {e}")
            return None
    else:
        print("未找到字典部分")
        return None

# 从obj的嵌套字典中提取
def extract_nested_dict(input_str):
    """
    从字符串中提取嵌套字典并解析为 Python 字典。
    
    参数:
        input_str (str): 包含嵌套字典的字符串，例如 
                         "对象: {'节点1': {'name': '巴宜区'}, '节点2': {'name': '临安区'}, '方向': 'None', '路径长度': '..3'},"
                         
    返回:
        dict: 提取并解析后的嵌套字典。
    """
    # 正则匹配嵌套字典部分
    match = re.search(r"\{.*\}", input_str)
    if match:
        dict_str = match.group(0)  # 提取匹配的嵌套字典字符串
        try:
            # 使用 ast.literal_eval 将字符串安全地转换为字典
            return ast.literal_eval(dict_str)
        except (ValueError, SyntaxError) as e:
            print(f"解析嵌套字典失败: {e}")
            return None
    else:
        print("未找到嵌套字典部分")
        return None

# 从返回形式提取
def extract_dict_from_three(input_str):
    """
    从字符串中提取字典部分并解析为 Python 字典。
    
    参数:
        input_str (str): 包含字典的字符串，例如 
                         "返回形式: {'总体形式': '对象属性', '聚合操作': [], '是否去重': '否', '是否排序': '不排序', '是否限制数量': '否', '是否跳过前几个': '否'}"
                         
    返回:
        dict: 提取并解析后的字典。
    """
    # 正则匹配大括号中的字典部分
    match = re.search(r"\{.*\}", input_str)
    if match:
        dict_str = match.group(0)  # 提取匹配的字典字符串
        try:
            # 使用 ast.literal_eval 将字符串安全地转换为字典
            return ast.literal_eval(dict_str)
        except (ValueError, SyntaxError) as e:
            print(f"解析字典失败: {e}")
            return None
    else:
        print("未找到字典部分")
        return None

# 后处理主函数
def post_intention_predict( intention_predicts ):
    intention_predict_post = []
    errors = []
    for i in range( len(intention_predicts)):
        # i = 0
        predicts = intention_predicts[i].strip(" \n")
        three_parts = predicts.split("\n")
        if len(three_parts) != 3:
            raise Exception( f"预测结果不是三部分 { three_parts }" )
        else:
            first_part = three_parts[0]
            if "路径长度" in first_part:
                obj = extract_nested_dict( first_part )
            else:
                obj = extract_dict_from_one( first_part )
            if obj == None:
                errors.append( (i, three_parts[0]))
            intens = {
                "对象": obj,
                "约束": three_parts[1].split( ":" )[1].strip(" ,"),
                "返回形式": extract_dict_from_three(three_parts[2])
            }
            intention_predict_post.append( intens )
    return intention_predict_post, errors



def show_intentions_pair( index, intention_labels, intention_predicts):
    print( f"Labels: {intention_labels[index]}")
    print( f"Predicts: {intention_predicts[index]}")


    