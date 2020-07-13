import imghdr
import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from comment.models import Comment, CommentImage
from myapp.libs.qiniuyun.qiniu_storage import storage
from myapp.settings import QINIU_URL
from myapp.utils.jwt import get_user_by_token
from user.models import Blog


class CommentUploadImageView(View):
    def post(self, request):
        image = request.FILES.get('image')
        # 查看前端上传的文件是否为图片,是返回图片类型,不是返回None
        type = imghdr.what(image)
        if type:
            img_url = QINIU_URL + storage(image.read())
        else:
            img_url = None
        return JsonResponse({'errmsg': 'ok', 'code': 0, "img_dict": {"comment_img": img_url}})


class CommentView(View):
    def post(self, request):
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': '请先登录', 'code': 201})
        dict = json.loads(request.body.decode())
        art_id = dict.get('art_id')
        image_url_list = dict.get('image_url_list')
        comment = dict.get('comment')
        blog_item = Blog.objects.filter(id=art_id)
        if len(blog_item) == 0:
            return JsonResponse({'errmsg': "博客不存在", 'code': 400})
        if not comment:
            return JsonResponse({'errmsg': '评论不能为空', 'code': 400})
        comment = Comment.objects.create(user=user, comment=comment, parent=None, ctime=datetime.now(),
                                         blog=blog_item[0])
        for image_url in image_url_list:
            CommentImage.objects.create(comment=comment, image=image_url)
        dict = comment.to_dict()
        dict['image_url_list'] = image_url_list
        return JsonResponse({'errmsg': 'ok', 'code': 0, 'comment': dict})

    def get(self, request):
        '''获取一级评论'''
        art_id = request.GET.get('art_id')
        comment_item = Comment.objects.filter(blog_id=art_id, parent=None)
        comment_list = []
        for comment in comment_item:
            dict = comment.to_dict()
            comment_image_item = CommentImage.objects.filter(comment=comment)
            image_list = []
            for comment_image in comment_image_item:
                image_list.append(comment_image.image)
            dict['image_url_list'] = image_list
            comment_list.append(dict)
        return JsonResponse({'errmsg': 'ok', 'code': 0, 'comment_list': comment_list})
