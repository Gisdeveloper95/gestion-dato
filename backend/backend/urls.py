"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.contrib import admin
from rest_framework.authtoken import views as token_views
from preoperacion import pdf_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('preoperacion/', include('preoperacion.urls')),
    path('postoperacion/', include('postoperacion.urls')),
    path('app/', include('app.urls')),
    path('scripts/', include('app.urls')), 
    path('api-token-auth/', token_views.obtain_auth_token),

    path('verificar_pdf/', pdf_views.verificar_pdf, name='verificar_pdf'),
    path('ver_pdf/', pdf_views.ver_pdf, name='ver_pdf'),
]
