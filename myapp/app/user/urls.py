from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^verify/(?P<uuid>\w{8}(-\w{4}){3}-\w{12})$', views.VerifyView.as_view()),
    re_path(r'^smscode$', views.SmsCodeView.as_view()),
    re_path(r'^login$', views.LoginView.as_view()),
    re_path(r'^user$', views.UserInfoView.as_view()),
    re_path(r'^user/articles$', views.UserAndArticleView.as_view()),
    re_path(r'^top$', views.ArticleTopView.as_view()),
    re_path(r'^blog$', views.AddBlogView.as_view()),
    re_path(r'^article/(?P<art_id>\d+)$', views.DelArticleView.as_view()),
    re_path(r'^wechat/upload$', views.ImageUploadView.as_view()),
    re_path(r'^attention/(?P<user_id>\d+)$', views.AttentionUserView.as_view()),
    re_path(r'^index$', views.IndexView.as_view()),
    re_path(r'^like/(?P<art_id>\d+)$', views.BlogLike.as_view()),
    re_path(r'^follow/(?P<art_id>\d+)$', views.BlogFollow.as_view()),
]
