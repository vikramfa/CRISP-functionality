"""batchapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
# from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view_yasg = get_schema_view(
    openapi.Info(
        title="Batches API",
        default_version='v0.0.0',
        description="This API allows one to Create Batch",
    ),
    public=True,
)

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^api-docs', schema_view_yasg.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^api/', include('rest_services.urls'), name='api_url'),
]