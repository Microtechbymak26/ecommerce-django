"""
URL configuration for store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include

# Import the home view from the ecommerce app
from ecommerce.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', home, name='home'),  # Home view from ecommerce app
    path('', include('ecommerce.urls')), # Assuming 'home' is the view function in ecommerce app
    path('user/', include('userauths.urls')),
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # CKEditor URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
