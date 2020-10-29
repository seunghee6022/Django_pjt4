from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.index, name= 'index'),
    path('<int:movie_pk>/review_list/', views.review_list, name= 'review_list'),
    path('<int:movie_pk>/create/', views.create, name= 'create'),
    path('<int:movie_pk>/<int:review_pk>/detail/', views.detail, name= 'detail'),
    path('<int:movie_pk>/<int:review_pk>/update/', views.update, name= 'update'),
    path('<int:movie_pk>/<int:review_pk>/delete/', views.delete, name= 'delete'),
    path('<int:movie_pk>/<int:review_pk>/comments/', views.comment_create, name= 'comment_create'),
    path('<int:movie_pk>/<int:review_pk>/comments/<int:comment_pk>/delete/', views.comment_delete, name= 'comment_delete'),
    path('<int:movie_pk>/<int:review_pk>/like/', views.like, name="like"),
]