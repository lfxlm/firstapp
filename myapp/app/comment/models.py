from django.db import models

# Create your models here.
from myapp.utils.dataset import datefunc
from user.models import Blog, User


class Comment(models.Model):
    '''评论表'''
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users', null=True)
    comment = models.CharField(max_length=1000, null=True, default=None)  # 评论内容
    reply_count = models.IntegerField(default=0)  # 评论回复数
    like_count = models.IntegerField(default=0)  # 点赞数
    ctime = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subs', default=None, null=True)

    class Meta:
        db_table = 't_comment'

    def to_dict(self):
        return {
            'id': self.id,
            'comment': self.comment,
            'reply_count': self.reply_count,
            'like_count': self.like_count,
            'ctime': datefunc(self.ctime),
            'username': self.user.username,
            'avatar': self.user.avatar,
        }


class CommentImage(models.Model):
    '''评论图片表'''
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='com')
    image = models.CharField(max_length=200)

    class Meta:
        db_table = 't_comment_image'
