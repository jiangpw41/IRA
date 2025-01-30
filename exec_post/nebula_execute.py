# ! pip install nebula3-python
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

# Nebula数据库配置
TimeOut = 10000
max_connection_pool_size = 10
user_name = 'root'
password = 'nebula'
db_url = '127.0.0.1'
db_port = 9669


def get_nebula_session():
    "获取nebula数据库session"
    config = Config()
    config.timeout = TimeOut                        
    MAX_CONNECTION_POOL_SIZE=max_connection_pool_size
    USERNAME=user_name
    PASSWORD=password
    config.max_connection_pool_size = MAX_CONNECTION_POOL_SIZE
    connection_pool = ConnectionPool()                          # Establish a connection pool
    ok = connection_pool.init([(db_url, db_port)], config)
    session = connection_pool.get_session(USERNAME, PASSWORD)
    return session


class DB_execute():
    def __init__(self, space_name):
        self.session = self.init_session()
        self.use_space( space_name )

    def init_session( self ):
        return get_nebula_session()

    def use_space(self, space_name ):
        use_result = self.exec( f"USE {space_name}")
        if not use_result.is_succeeded():
            raise Exception( f"切换到Space {space_name}失败！") 
        '''else:
            print( f"切换到Space {space_name}成功，当前space情况如下：")
            print(f"""
                当前全部Space为：{self.exec( f"Show Spaces" )}，其中：
                {space_name}的Vertex有：{self.exec( f"Show TAGs" )}
                {space_name}的Edges有：{self.exec( f"Show Edges" )}""")'''
        # db_executor( f"DESCRIBE SPACE nba" )

    def exec( self, query):
        try:
            result = self.session.execute( query )
            '''if not result.is_succeeded():
            print( f"执行失败：{result.error_code()}")
            # print( query )'''
        except:
            result = None
        return result
    
if __name__ == "__main__":
    executor = DB_execute( "nba")