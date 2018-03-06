from models import Model
from models.comment import Comment


class Weibo(Model):
    """
    微博类
    """
    def __init__(self, form, user_id=-1):
        super().__init__(form)
        self.content = form.get('content', '')
        # 和别的数据关联的方式, 用 user_id 表明拥有它的 user 实例
        self.user_id = form.get('user_id', user_id)

    def is_owner(self, id):
        return self.user_id == id

    def comments(self):
        return Comment.find_all(weibo_id=self.id)

    @classmethod
    def update(cls, id, form):
        w = cls.find(id)
        valid_names = [
            'content',
        ]
        for key in form:
            # 这里只应该更新我们想要更新的东西
            if key in valid_names:
                setattr(w, key, form[key])
        w.save()