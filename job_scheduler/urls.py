from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.list_jobs, name='list_jobs'),
    path('<int:job_id>/', views.detail, name='detail'),
]
