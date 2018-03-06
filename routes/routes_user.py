from models.session import Session
from routes import (
    random_str,
    redirect,
    http_response
)
from utils import log
from utils import template
from models.user import User
import sqlite3


def route_login(request):
    """
    登录页面的路由函数
    """
    log('login, cookies', request.cookies)
    if request.method == 'POST':
        form = request.form()
        u = User(form)
        if u.validate_login():
            session_id = random_str()
            u = User.find_by(username=u.username)
            s = Session.new(dict(
                session_id=session_id,
                user_id=u.id,
            ))
            s.save()
            log('session', s)
            headers = {
                'Set-Cookie': 'sid={}'.format(session_id)
            }
            # 登录后定向到 /
            return redirect('/', headers)
    # 显示登录页面
    body = template('login.html')
    return http_response(body)


def route_register(request):
    """
    注册页面的路由函数
    """
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            # 注册成功后 定向到登录页面
            return redirect('/login')
        else:
            # 注册失败 定向到注册页面
            return redirect('/register')
    # 显示注册页面
    body = template('register.html')
    return http_response(body)


def edit_password(request):
    user_id = int(request.query.get('id', -1))
    log('edit_password', user_id)
    u = User.find(user_id)
    # 替换模板文件中的标记字符串
    body = template('admin_password_edit.html', user=u)
    return http_response(body)


def update_user_password(request):
    form = request.form()
    user_id = int(form.get('id'))
    log('update_user_password', form.get('id'))
    # user_id = int(form['id'])
    User.update(user_id, form)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/')


def route_dict():
    r = {
        '/login': route_login,
        '/register': route_register,
        '/password': edit_password,
        '/password/update': update_user_password,
    }
    return r


