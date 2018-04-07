# 基于 Socket的 Web Server 框架
## 基于MVC架构，采用Python Socket包和HTTP协议实现了一个完整的Web Server

models文件夹下为ORM框架

routes文件夹存放的是路由处理函数，用字典实现的路由分发

template存放基于Jinja2模板语言的html文件

static存放静态文件

data文件夹保存用户数据


以下是routes_todo.py中的路由分发函数：
```python
def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/todo/index': login_required(index),
        '/todo/add': login_required(add),
        '/todo/delete': login_required(same_user_required(delete)),
        '/todo/edit': login_required(same_user_required(edit)),
        '/todo/update': login_required(same_user_required(update)),
    }
    return d
```

request.py是处理浏览器发过来的request请求的文件，用一个Request类来解析请求行、请求首部、请求体。以下是其中的一部分代码：
```python
class Request(object):
    def __init__(self, raw_data):
        # 只能 split 一次，因为 body 中可能有换行
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        path = parts[1]
        self.path = ""
        self.query = {}
        self.parse_path(path)
        log('Request: path 和 query', self.path, self.query)

        self.headers = {}
        self.cookies = {}
        self.add_headers(h[1:])
        self.add_cookies()
        log('Request: headers 和 cookies', self.headers, self.cookies)

```

server.py为服务启动文件，通过创建socket，然后bind绑定主机和端口，listen监听，accept接收浏览器发过来的数据，调用request.py的Request类解析出path路径，根据 path 调用routes文件夹中相应的处理函数，生成response响应，把响应通过connection.sendall发送给客户端。以下是其中的部分代码：
```python
def response_for_path(request):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    r = {}
    # 注册外部的路由
    r.update(todo_routes())
    r.update(weibo_routes())
    r.update(user_routes())
    r.update(static_routes())
    response = r.get(request.path, error)
    return response(request)


def process_request(connection):
    r = connection.recv(1024)
    r = r.decode()
    log('request log:\n{}'.format(r))
    # 把原始请求数据传给 Request 对象
    request = Request(r)
    # 用 response_for_path 函数来得到 path 对应的响应内容
    response = response_for_path(request)
    # 把响应发送给客户端
    connection.sendall(response)
    # 处理完请求, 关闭连接
    connection.close()


def run(host, port):
    """
    启动服务器
    """
    # 初始化 socket 
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    log('开始运行于', '{}:{}'.format(host, port))
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        # 无限循环来处理请求
        while True:
            connection, address = s.accept()
            # 第二个参数类型必须是 tuple
            log('ip {}'.format(address))
            _thread.start_new_thread(process_request, (connection,))


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='127.0.0.1',
        port=3000,
    )
    run(**config)

```

