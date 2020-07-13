from django.urls import re_path

from . import views

urlpatterns = [
   re_path(r"^comment/upload$",views.CommentUploadImageView.as_view()),
   re_path(r"^comment$",views.CommentView.as_view()),
]
