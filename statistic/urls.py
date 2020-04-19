from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('repository/<slug:owner>/<slug:name>', views.repository, name='repository'),
    path('repository/<slug:owner>/<slug:name>/<int:month>/<int:day>/<int:year>/', views.commits, name='commits')
]