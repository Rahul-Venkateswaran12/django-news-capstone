"""
URL configuration for the news_project application.

This module defines the URL routing for the news_project Django application.
The `urlpatterns` list maps URLs to views, including the admin interface and
the news app URLs. For more details, see:
https://docs.djangoproject.com/en/5.2/topics/http/urls/

Examples:
    - Function views: Import views and add `path('', views.home, name='home')`.
    - Class-based views: Use `path('', Home.as_view(), name='home')`.
    - Including URLconf: Use `path('blog/', include('blog.urls'))`.

"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
