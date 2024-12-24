"""
URL configuration for product_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from product_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name="index"),
    path('', views.signin, name='signin'),
    path('register/', views.register, name='register'),
    path('products/', views.products, name='products'),
    # branch
    path('branch_list/', views.branch_list, name='branch_list'),
    path('branch/create/', views.create_branch, name='create_branch'),
    path('update/<int:branch_id>/', views.update_branch, name='update_branch'),
    path('delete/<int:branch_id>/', views.delete_branch, name='delete_branch'), 
    # turul
    path('turul_list/', views.turul_list, name='turul_list'), 
    path('turul/create/', views.create_turul, name='create_turul'),
    path('turul/update/<int:turul_id>/', views.update_turul, name='update_turul'),
    path('turul/delete/<int:turul_id>/', views.delete_turul, name='delete_turul'),
    # worker
    path('worker_list/', views.worker_list, name='worker_list'),  # List all workers
    path('worker/create/', views.create_worker, name='create_worker'),  # Create a new worker
    path('worker/update/<int:worker_id>/', views.update_worker, name='update_worker'),
    path('worker/delete/<int:worker_id>/', views.delete_worker, name='delete_worker'),  # Delete a specific worker
    path('settings/', views.settings, name='settings'),
    path('report/', views.report, name='report'),
    path('notifications/', views.notifications, name='notifications'),
]
