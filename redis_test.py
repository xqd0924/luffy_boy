# import redis
# # 拿到一个redis 的链接
# conn=redis.Redis('127.0.0.1',6379)

# print(conn.get('name'))
# redis 的字符串操作
# set方法set(name, value, ex=None, px=None, nx=False, xx=False)
# conn.set('token','1232sdsfdasdfa',ex=5)
# conn.set('name','egon',nx=False)
# conn.set('age','13',xx=True)
# conn.setex('token',5,'ddddd')
# conn.mset({'k1':'11','k2':22})

# print(conn.get('k1'))
# print(conn.mget('k1','k2'))
# print(conn.mget({'k1','k2'}))

# conn.set('name','刘清政')
# 一个汉字占三个字节,前闭后闭区间
# 取出字符串指定某部分
# print(conn.getrange('name',0,2).decode('utf-8'))
# print(conn.strlen('name'))
# conn.incr('k1',-2)
# conn.append('k1',11)


# 掌握的:set get  mset mget  append   incr   getrange(前闭后闭区间)  strlen



# 连接池:
import redis
# 拿到一个reids的连接池
pool=redis.ConnectionPool(host='127.0.0.1',port=6379,max_connections=5)
# 从池子中拿一个链接
conn=redis.Redis(connection_pool=pool)
print(conn.get('name').decode('utf-8'))




