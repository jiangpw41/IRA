import signal
from tqdm import tqdm
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError
import os
from wayne_utils import load_data, save_data


# 设置超时异常
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Query timed out!")

# 执行数据库
def neo4j_excecute( query ):
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "123456"
    # 配置连接参数
    connection_config = {
        "max_transaction_retry_time": 30.0,  # 事务重试最大时间（秒）
        "connection_timeout": 30.0,          # 连接超时时间
        "connection_acquisition_timeout": 30.0,  # 获取连接超时时间
        "max_connection_lifetime": 30.0,     # 连接最大生命周期
        # "connection_pool_size": 50           # 连接池大小（可选）
    }
    driver = GraphDatabase.driver(uri, auth=(username, password), **connection_config)
    database_name = "graph-all02.db"# "cyspider"

    with driver.session( database=database_name) as session:
        ans = list( session.run(query) )
    return ans

def result_catch(query, debug=False):
    "三种返回结果：列表（正常返回）、字符串（语法、超时、其他错误）、"
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 设置30秒的超时限制
    try:
        ans = neo4j_excecute( query )
        return ans
    except CypherSyntaxError as e:
        if debug:
            print( "语法错误")
        return "语法错误"
    except TimeoutException:
        print( "超时30秒")
        return "超时错误"
    except:
        if debug:
            print( "其他错误")
        return "其他错误"
    finally:
        signal.alarm(0)




def Neo4j_Execute_Batch( query_list ):
    ret_list = []
    for i in tqdm( range( len(query_list) ), f"Executing queries on neo4j..."):
        ret_list.append( result_catch( query_list[i] ) )
    return ret_list




if __name__ == "__main__":
    from neo4j_pre_post import Neo4j_Pre_Process, Neo4j_Execute_Post
    query = "match (:ENTITY{name:'鲁迅'})<--(h)-[:Relationship{name:'别名'}]->(q) return distinct q.name limit 1"
    ans = neo4j_excecute( query )