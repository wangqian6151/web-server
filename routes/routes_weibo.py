from models.comment import Comment
from models.user import User
from models.weibo import Weibo
from routes import (
    redirect,
    http_response,
    current_user,
    login_required,
)
from utils import template, log


# 微博相关页面
def index(request):
    author_id = int(request.query.get('user_id', -1))
    user = current_user(request)
    if author_id == -1:
        author_id = user.id

    weibos = Weibo.find_all(user_id=author_id)
    # weibos = Weibo.all()
    body = template('weibo_index.html', weibos=weibos, user=user)
    return http_response(body)


def new(request):
    body = template('weibo_new.html')
    return http_response(body)


def add(request):
    u = current_user(request)
    # 创建微博
    form = request.form()
    w = Weibo.new(form)
    w.user_id = u.id
    w.save()
    return redirect('/weibo/index')


def delete(request):
    u = current_user(request)
    # 删除微博
    weibo_id = int(request.query.get('id', None))
    Weibo.delete(weibo_id)
    return redirect('/weibo/index')


def comment_delete(request):
    u = current_user(request)
    # 删除微博
    comment_id = int(request.query.get('id', None))
    c = Comment.find(comment_id)
    log('comment_delete 1', c.user_id)
    w = Weibo.find(c.weibo_id)
    log('comment_delete 2', w.user_id)
    if c.user_id == u.id or w.user_id == u.id:
        Comment.delete(comment_id)
    return redirect('/weibo/index')


# def edit(request):
#     weibo_id = int(request.query.get('id', -1))
#     w = Weibo.find(weibo_id)
#     # 生成一个 edit 页面
#     body = template('weibo_edit.html', weibo_id=w.id, weibo_content=w.content)
#     return http_response(body)


def edit(request):
    weibo_id = int(request.query.get('id', -1))
    w = Weibo.find(weibo_id)
    # 替换模板文件中的标记字符串
    body = template('weibo_edit.html', weibo=w)
    return http_response(body)


def comment_edit(request):
    comment_id = int(request.query.get('id', -1))
    c = Comment.find(comment_id)
    # 替换模板文件中的标记字符串
    body = template('comment_edit.html', comment=c)
    return http_response(body)


# def update(request):
#     u = current_user(request)
#     form = request.form()
#     content = form.get('content', '')
#     weibo_id = int(form.get('id', -1))
#     w = Weibo.find(weibo_id)
#     w.content = content
#     w.save()
#     # 重定向到用户的主页
#     return redirect('/weibo/index')

def update(request):
    """
    用于修改 weibo 的路由函数
    """
    form = request.form()
    weibo_id = int(form.get('id'))
    Weibo.update(weibo_id, form)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def comment_update(request):
    """
    用于修改 comment 的路由函数
    """
    form = request.form()
    comment_id = int(form.get('id'))
    Comment.update(comment_id, form)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def comment_add(request):
    u = current_user(request)
    # 创建微博
    form = request.form()
    c = Comment.new(form)
    c.user_id = u.id
    c.save()
    log('comment add', c, u, form)
    weibo = Weibo.find(id=int(form['weibo_id']))
    return redirect('/weibo/index?user_id={}'.format(weibo.user_id))


def same_user_required(route_function):
    def f(request):
        log('weibo same user required', request)
        u = current_user(request)
        if request.method == 'GET':
            weibo_id = int(request.query.get('id'))
        else:
            weibo_id = int(request.form().get('id'))
        w = Weibo.find(weibo_id)
        if w.is_owner(u.id):
            return route_function(request)
        else:
            return redirect('/login')

    return f


def same_user_required_for_comment(route_function):
    def f(request):
        log('comment same user required', request)
        u = current_user(request)
        if request.method == 'GET':
            comment_id = int(request.query.get('id'))
        else:
            comment_id = int(request.form().get('id'))
        c = Comment.find(comment_id)
        if c.is_owner(u.id):
            return route_function(request)
        else:
            return redirect('/login')

    return f


def route_dict():
    r = {
        '/weibo/index': login_required(index),
        '/weibo/new': login_required(new),
        '/weibo/edit': login_required(same_user_required(edit)),
        '/weibo/add': login_required(add),
        '/weibo/update': login_required(same_user_required(update)),
        '/weibo/delete': login_required(same_user_required(delete)),
        # 评论功能
        '/comment/add': login_required(comment_add),
        '/comment/delete': login_required(comment_delete),
        '/comment/edit': login_required(same_user_required_for_comment(comment_edit)),
        '/comment/update': login_required(same_user_required_for_comment(comment_update)),
    }
    return r
