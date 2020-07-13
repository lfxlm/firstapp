from django.contrib.auth.models import AbstractUser
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True)
    username = models.CharField(max_length=20, default=mobile, unique=True)
    blog_count = models.IntegerField(default=0)
    follow_count = models.IntegerField(default=0)
    fans_count = models.IntegerField(default=0)
    avatar = models.CharField(max_length=500, default=None, null=True)
    info = models.CharField(max_length=100, default="此人很懒,什么也没有留下~", null=True)

    class Meta:
        db_table = 't_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'blog_count': self.blog_count,
            'follow_count': self.follow_count,
            'fans_count': self.fans_count,
            'avatar': self.avatar,
            'info': self.info,
        }


class Relation(models.Model):
    '''用户关注表'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='关注者', related_name='user')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='被关注者', related_name='author_user')
    relation = models.IntegerField(default=1, verbose_name='关系')  # 1.关注,0.无关系,2.拉黑

    class Meta:
        db_table = 't_relation'
        verbose_name = '用户关系表'
        verbose_name_plural = verbose_name


class BlogContent(models.Model):
    content = RichTextUploadingField(default='', verbose_name='文章内容')

    class Meta:
        db_table = 't_content'
        verbose_name = '博客内容表'
        verbose_name_plural = verbose_name


class Blog(models.Model):
    title = models.CharField(max_length=100, null=True)
    content = models.ForeignKey(BlogContent, on_delete=models.CASCADE, related_name='blog_content')
    ctime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog')
    comment_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    image1 = models.CharField(max_length=500, verbose_name='封面图1', default=None, null=True)
    image2 = models.CharField(max_length=500, verbose_name='封面图2', default=None, null=True)
    image3 = models.CharField(max_length=500, verbose_name='封面图3', default=None, null=True)
    is_top = models.IntegerField(default=0, null=True)  # 是否置顶,0.不置顶,1.置顶
    is_del = models.IntegerField(default=0, null=True)  # 是否删除,0,不删除,1.删除

    class Meta:
        db_table = 't_blog'
        verbose_name = '博客表'
        verbose_name_plural = verbose_name

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user.id,
            'title': self.title,
            'content': self.content.content,
            'username': self.user.username,
            'avatar': self.user.avatar,
            'comment_count': self.comment_count,
            'like_count': self.like_count,
            'time': self.updatetime.strftime('%Y-%m-%d %H:%M:%S'),
            'is_top': self.is_top,
        }


class UserFollow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True)
    is_follow = models.IntegerField(default=0, null=True)  # 0.无态度,1.收藏

    class Meta:
        db_table = 't_user_follow_blog'
        verbose_name = '用户博客收藏表'
        verbose_name_plural = verbose_name


class UserLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True)
    is_like = models.IntegerField(default=0, null=True)  # 0.无态度,1.点赞

    class Meta:
        db_table = 't_user_like_blog'
        verbose_name = '用户博客收藏表'
        verbose_name_plural = verbose_name
