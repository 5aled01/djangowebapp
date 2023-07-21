# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from django.conf.urls.static import static

from core import settings
from .views import login_view, register_user
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    #path('register/', register_user, name="register"),
    path('profile', views.edit_profile, name='edit_profile'),
    path("logout/", LogoutView.as_view(), name="logout")
]
if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)