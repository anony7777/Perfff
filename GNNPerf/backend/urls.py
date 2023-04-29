from django.urls import path
from . import views

urlpatterns = [
    path('queryProjectNames/', views.queryProjectNames, name='queryProjectNames'),
    path('queryProject/', views.queryProject, name='queryProject'),
    path('newProject/', views.newProject, name='newProject'),
    path('renameProject/', views.renameProject, name='renameProject'),
    path('saveProject/', views.saveProject, name='saveProject'),
    path('deleteProject/', views.deleteProject, name='deleteProject'),
    path('compile/', views.compile, name='compile'),
    path('train/', views.train, name='train'),
    path('queryResultInfos/', views.queryResultInfos, name='queryResultInfos'),
    path('queryCmd/', views.queryCmd, name='queryCmd'),
    path('deleteResult/', views.deleteResult, name='deleteResult'),
    path('getResult/', views.getResult, name='getResult')
]