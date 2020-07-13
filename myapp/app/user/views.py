import imghdr
import json
import random
import re
from datetime import datetime, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from myapp.libs.captcha.captcha import captcha
from myapp.libs.qiniuyun.qiniu_storage import storage
from myapp.settings import QINIU_URL
from myapp.utils.dataset import datefunc
from myapp.utils.jwt import generate_jwt, get_user_by_token
from user.models import User, Blog, Relation, BlogContent, UserLike, UserFollow


class VerifyView(View):
    def get(self, request, uuid):
        # print(uuid)
        text, image = captcha.generate_captcha()
        print(text)
        img_url = storage(image)
        redis_conn = get_redis_connection('verify')
        redis_conn.setex('uuid:%s' % uuid, 600, text)
        return JsonResponse({'errmsg': 'ok', 'code': 0, 'img_verify': QINIU_URL + img_url, 'text': text})


class SmsCodeView(View):
    def get(self, request):
        dict = request.GET
        mobile = dict.get('mobile')
        uuid = dict.get('uuid')
        verify = dict.get("verify")
        if not re.match(r'[1][3-9][0-9]{9}', mobile):
            return JsonResponse({'errmsg': '请输入正确的手机号码', 'code': 400})
        redis_conn = get_redis_connection('verify')
        pl = redis_conn.pipeline()
        img_code = redis_conn.get('uuid:%s' % uuid)
        if not img_code:
            return JsonResponse({'errmsg': '图形验证码不存在或者已过期,请重试', 'code': 400})
        img_code = img_code.decode()
        if not img_code.upper() == verify.upper():
            return JsonResponse({"errmsg": '验证码输入错误,请重新输入', 'code': 400})
        # 发送短信的程序...
        num = random.randint(100000, 999999)
        print(num)
        pl.setex("mobile:%s" % mobile, 300, num)
        pl.delete('uuid:%s' % uuid)
        pl.execute()
        return JsonResponse({'errmsg': 'ok', 'code': 0, 'sms_code': num})


class LoginView(View):
    def post(self, request):
        dict = json.loads(request.body.decode())
        mobile = dict.get('mobile')
        sms_code = dict.get('sms_code')
        # uuid = dict.get('uuid')
        redis_conn = get_redis_connection('verify')
        sms_code_server = redis_conn.get("mobile:%s" % mobile)
        if not sms_code_server:
            return JsonResponse({'errmsg': '短信验证码已过期', 'code': 400})
        sms_code_server = sms_code_server.decode()
        if sms_code_server != sms_code:
            return JsonResponse({'errmsg': '短信验证码错误,请重试', 'code': 201})
        if not re.match(r'[1][3-9][0-9]{9}', mobile):
            return JsonResponse({'errmsg': '请输入正确的手机号码', 'code': 400})
        item = User.objects.filter(mobile=mobile)
        if len(item) == 0:
            user = User.objects.create(username=mobile, mobile=mobile, last_login=datetime.now())
            user.save()
        else:
            item.update(last_login=datetime.now())
        user_id = item[0].id if len(item) != 0 else user.id
        username = item[0].username if len(item) != 0 else user.username
        token = generate_jwt(user_id)
        return JsonResponse({'errmsg': 'ok', 'code': 0, "user_id": user_id, 'username': username, 'token': token})


class UserInfoView(View):
    def get(self, request):
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': '登陆已失效,请重新登陆', 'code': 201})
        dict = user.to_dict()
        return JsonResponse({'errmsg': 'ok', 'code': 0, 'item': dict})


class UserAndArticleView(View):
    def get(self, request):
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': '请先登录', 'code': 201})
        user_dict = user.to_dict()
        items = Blog.objects.filter(user=user, is_del=0)
        article_items = []
        for item in items:
            dict = item.to_dict()
            if item.is_top != 1:
                article_items.append(dict)
            else:
                article_items.insert(0, dict)
        return JsonResponse({'errmsg': "ok", 'code': 0, 'user_dict': user_dict, 'article_items': article_items})


class ArticleTopView(View):
    def post(self, request):
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': '请先登录', 'code': 201})
        # 把所有置顶取消
        Blog.objects.filter(user=user, is_del=0).update(is_top=0)
        art_id = json.loads(request.body.decode()).get('article_id')
        if not art_id:
            return JsonResponse({'errmsg': '缺少参数', 'code': 400})
        items = Blog.objects.filter(id=art_id, is_del=0)
        if len(items) == 0:
            return JsonResponse({'errmsg': '文章id无效', 'code': 400})
        items.update(is_top=1)

        user_dict = user.to_dict()
        items = Blog.objects.filter(user=user, is_del=0)
        article_items = []
        for item in items:
            dict = item.to_dict()
            if item.is_top != 1:
                article_items.append(dict)
            else:
                article_items.insert(0, dict)
        return JsonResponse({'errmsg': "ok", 'code': 0, 'user_dict': user_dict, 'article_items': article_items})


class DelArticleView(View):
    def delete(self, request, art_id):
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': '请先登录', 'code': 201})
        items = Blog.objects.filter(id=art_id, is_del=0)
        if len(items) == 0:
            return JsonResponse({'errmsg': '文章id无效', 'code': 400})
        items.update(is_del=1)

        user_dict = user.to_dict()
        items = Blog.objects.filter(user=user, is_del=0)
        article_items = []
        for item in items:
            dict = item.to_dict()
            if item.is_top != 1:
                article_items.append(dict)
            else:
                article_items.insert(0, dict)
        return JsonResponse({'errmsg': "ok", 'code': 0, 'user_dict': user_dict, 'article_items': article_items})


class AddBlogView(View):
    def put(self, request):
        content = json.loads(request.body.decode()).get('content')
        img_list = re.findall('img src="(.*?)"', content, re.S)
        title = json.loads(request.body.decode()).get('title')
        if not content:
            return JsonResponse({'errmsg': '缺少参数', 'code': 400})
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({"errmsg": '请先登录', 'code': 201})
        blog_content = BlogContent.objects.create(content=content)
        blog = Blog.objects.create(content_id=blog_content.id, ctime=datetime.now() + timedelta(hours=8), user=user,
                                   title=title)
        try:
            blog.image1 = img_list[0]
            blog.image2 = img_list[1]
            blog.image3 = img_list[2]
            blog.save()
        except Exception as e:
            blog.save()
        return JsonResponse({'errmsg': 'ok', 'code': 0})

    def post(self, request):
        id = json.loads(request.body.decode()).get('id')
        if not id:
            return JsonResponse({'errmsg': 'error', 'code': 400})
        user = get_user_by_token(request)
        blog = Blog.objects.get(id=id)
        if not user:
            relation = []
            isshowlike = 1
        else:
            relation = Relation.objects.filter(user=user, author=blog.user, relation=1)
            isshowlike = 0 if user.id == blog.user.id else 1
        # 查询用户有没有点赞收藏文章
        '''点赞'''
        item = UserLike.objects.filter(user=user, blog=blog, is_like=1)
        if len(item) == 0:
            like_art = 0
        else:
            like_art = 1
        '''收藏'''
        item = UserFollow.objects.filter(user=user, blog=blog, is_follow=1)
        if len(item) == 0:
            follow_art = 0
        else:
            follow_art = 1
        return JsonResponse({'errmsg': 'ok', 'code': 0, 'data': blog.to_dict(),
                             'flag': 1 if len(relation) > 0 else 0, 'isshowlike': isshowlike,
                             'like_art': like_art, 'follow_art': follow_art})


class ImageUploadView(View):
    def post(self, request):
        image = request.FILES.get('image')
        # 查看前端上传的文件是否为图片,是返回图片类型,不是返回None
        type = imghdr.what(image)
        if type:
            img_url = QINIU_URL + storage(image.read())
        else:
            img_url = None
        return JsonResponse({'errmsg': 'ok', 'code': 0, "img_url": img_url})


class AttentionUserView(View):
    def post(self, request, user_id):
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': 'error', 'code': 201})
        items = Relation.objects.filter(user=user, author_id=user_id)
        if len(items) == 0:
            Relation.objects.create(user=user, author_id=user_id)
        else:
            items.update(relation=1)
        return JsonResponse({'errmsg': 'ok', 'code': 0})

    def delete(self, request, user_id):
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': 'error', 'code': 201})
        items = Relation.objects.filter(user=user, author_id=user_id, relation=1)
        if len(items) == 0:
            Relation.objects.create(user=user, author_id=user_id, relation=0)
        else:
            items.update(relation=0)  # 0:不关注,1:关注,2:拉黑
        return JsonResponse({'errmsg': 'ok', 'code': 0})


class IndexView(View):
    def get(self, request):
        blog_items = Blog.objects.filter(is_del=0).order_by('-updatetime')
        blog_list = []
        for blog in blog_items:
            blog_list.append({
                'id': blog.id,
                'title': blog.title,
                'username': blog.user.username,
                'comment_count': blog.comment_count,
                'time': datefunc(blog.updatetime),
                'image1': blog.image1,
                'image2': blog.image2,
                "image3": blog.image3
            })
        return JsonResponse({'errmsg': 'ok', 'code': 0, 'blog_list': blog_list})


class BlogLike(View):
    def post(self, request, art_id):
        blog_item = Blog.objects.filter(id=art_id)
        if len(blog_item) == 0:
            return JsonResponse({'errmsg': '博客不存在', 'code': 400})
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': '点赞需要登录哦', 'code': 201})
        relation = UserLike.objects.filter(blog=blog_item[0], user=user)
        if len(relation) > 0:
            if relation[0].is_like == 0:  # 存在但是无态度
                relation.update(is_like=1)  # 改成点赞状态
            else:
                # 存在且为点赞状态,改成无态度
                relation.update(is_like=0)
        else:
            UserLike.objects.create(user=user, blog=blog_item[0], is_like=1)
        return JsonResponse({'errmsg': 'ok', 'code': 0})


class BlogFollow(View):
    def post(self, request, art_id):
        blog_item = Blog.objects.filter(id=art_id)
        if len(blog_item) == 0:
            return JsonResponse({'errmsg': '博客不存在', 'code': 400})
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': '点赞需要登录哦', 'code': 201})
        relation = UserFollow.objects.filter(blog=blog_item[0], user=user)
        if len(relation) > 0:
            if relation[0].is_follow == 0:  # 存在但是无态度
                relation.update(is_follow=1)  # 改成点赞状态
            else:
                # 存在且为点赞状态,改成无态度
                relation.update(is_follow=0)
        else:
            UserFollow.objects.create(user=user, blog=blog_item[0], is_follow=1)
        return JsonResponse({'errmsg': 'ok', 'code': 0})
