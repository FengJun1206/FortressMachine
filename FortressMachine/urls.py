"""FortressMachine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('web_ssh/', views.web_ssh, name='web_ssh'),
    path('host_list/', views.host_list, name='host_list'),
    path('batch_task/', views.batch_task, name='batch_task'),
    path('get_task_result/', views.get_task_result, name='get_task_result'),

    path('file_transfer/', views.file_transfer, name='file_transfer'),

    path('audit_log/', views.audit_log, name='audit_log'),

    path('host_result_history/', views.host_result_history, name='host_result_history'),

    path('account_login/', views.account_login, name='account_login'),
    path('account_logout/', views.account_logout, name='account_logout'),
]
