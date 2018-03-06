from models.todo import Todo
from routes import (
    redirect,
    http_response,
    current_user,
    login_required,
)
from utils import template, log


# 直接写函数名字不写 route 了
def index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    u = current_user(request)
    todo_list = Todo.find_all(user_id=u.id)
    body = template('todo_index.html', todos=todo_list)
    return http_response(body)


def edit(request):
    """
    todo 首页的路由函数
    """
    todo_id = int(request.query.get('id'))
    t = Todo.find_by(id=todo_id)
    # 替换模板文件中的标记字符串
    body = template('todo_edit.html', todo=t)
    return http_response(body)


def add(request):
    """
    接受浏览器发过来的添加 todo 请求
    添加数据并发一个 302 定向给浏览器
    浏览器就会去请求 / 从而回到主页
    """
    # 得到浏览器发送的表单
    form = request.form()
    # 创建一个 todo
    u = current_user(request)
    log('add user', u)
    Todo.new(form, u.id)
    # 让浏览器刷新页面到主页去
    return redirect('/todo/index')


def update(request):
    """
    用于增加新 todo 的路由函数
    """
    form = request.form()
    todo_id = int(form.get('id'))
    Todo.update(todo_id, form)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/todo/index')


def delete(request):
    """
    通过下面这样的链接来删除一个 todo
    /delete?id=1
    """
    todo_id = int(request.query.get('id'))
    Todo.delete(todo_id)
    return redirect('/todo/index')


def same_user_required(route_function):
    def f(request):
        log('same user required', request)
        u = current_user(request)
        if request.method == 'GET':
            todo_id = int(request.query.get('id'))
        else:
            todo_id = int(request.form().get('id'))
        t = Todo.find(todo_id)
        if t.is_owner(u.id):
            return route_function(request)
        else:
            return redirect('/login')

    return f


def route_dict():
    d = {
        '/todo/index': login_required(index),
        '/todo/add': login_required(add),
        '/todo/delete': login_required(same_user_required(delete)),
        '/todo/edit': login_required(same_user_required(edit)),
        '/todo/update': login_required(same_user_required(update)),
    }
    return d
