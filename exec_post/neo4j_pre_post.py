from tqdm import tqdm
import neo4j


# 对大模型生成的Cypher进行简单预处理
def Neo4j_Pre_Process(test_list_raw):
    ret_list = []
    for i in range(len(test_list_raw)):
        cypher = test_list_raw[i]
        flag = 0
        for match in [ "match ", "Match "]:     # 如果是Match子句，截取该部分
            if match in cypher:
                post_part = "match " + cypher.split( match )[1].strip()
                if post_part.endswith( "\"" ):
                    core_part = post_part.split( "\"" )[0].strip()
                    ret_list.append( core_part )
                else:
                    ret_list.append( post_part )
                flag = 1
                break
        if flag == 0:                           # 如果不是Match子句，则简单strip()一下
            if cypher.strip() == "":
                cypher = " "
            ret_list.append( cypher )
    return ret_list

# 处理Record类型中的Path子类型
def process_path_obj( value ):
    path_str = ""                               # value最后返回的形式是字符串
    path＿relation_list = list( value )         # path对象的所有relation
    
    last_node_name = ""
    for sub_relation in path＿relation_list:
        start_node_name = list(sub_relation.start_node.values())[0]
        end_node_name = list(sub_relation.end_node.values())[0]
        rel_label = sub_relation.type
        # 判断该边是不是第一条边
        if path_str == "":
            path_str = f'({start_node_name})-[:{rel_label} {{}}]->({end_node_name})'
        else:
            if last_node_name == end_node_name:
                append_str = f"<-[:{rel_label} {{}}]-({start_node_name})"
            elif last_node_name == start_node_name:
                append_str = f"-[:{rel_label} {{}}]->({end_node_name})"
            else:
                raise Exception(f"路径方向不对{path＿relation_list}")
            path_str = path_str + append_str
        last_node_name = end_node_name
    return path_str

def process_node_relation_obj( value ):
    ret_dict = {}
    for item in list(value.items()):
        ret_dict[ item[0] ] = item[1]
    return ret_dict

# 对执行db完毕的结果进行后处理：保留所有字符串类型的结果
def Neo4j_Execute_Post( execute_result_list ):
    post_result_list = [ ]
    not_list = []
    not_record = []
    # 遍历
    for i in tqdm( range(len(execute_result_list)), desc="Post"):
        line = execute_result_list[i]
        # 如果是字符串：语法错误、其他错误等
        if isinstance( line, str):
            post_result_list.append( line )
        elif not isinstance( line, list):
            not_list.append( i )
            post_result_list.append( "" )
        else:
            record_dict_list = []
            for record in line:
                # 遍历record列表中每个Record对象
                if isinstance( record, neo4j._data.Record ):
                    record_dict = {}
                    for item in record.items():
                        key, value = item[0], item[1]
                        if isinstance( value, list):
                            if len(value) == 0:
                                continue
                            elif isinstance( value[0], neo4j.graph.Relationship):
                                # print( len(value) )
                                temp = []
                                for rel in value:
                                    temp.append( process_node_relation_obj( rel ) )
                                record_dict[key] = temp
                        elif isinstance( value, neo4j.graph.Relationship) or isinstance( value, neo4j.graph.Node):
                            record_dict[key] = process_node_relation_obj( value )
                        elif isinstance( value, neo4j.graph.Path):
                            record_dict[key] = process_path_obj( value )
                        else:
                            record_dict[key] = value
                    record_dict_list.append(record_dict  )
                else:
                    not_record.append( i )
            post_result_list.append( record_dict_list )
    return post_result_list, not_list, not_record

if __name__=="__main__":
    print("")