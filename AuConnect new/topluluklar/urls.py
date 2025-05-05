from django.urls import path
from . import views

urlpatterns = [
    path("", views.liste, name="topluluklar"),
    path("topluluk/<int:topluluk_id>/", views.topluluk_detail, name="topluluk_detail"),
    path("post/create/", views.create_post, name="create_post"),
    path("post/edit/<int:post_id>/", views.edit_post, name="edit_post"),
    path("post/delete/<int:post_id>/", views.delete_post, name="delete_post"),
    path("anasayfa-posts/", views.anasayfa_posts, name="anasayfa_posts"),
    path("api/posts/<int:post_id>/", views.post_api_detail, name="post_api_detail"),
]