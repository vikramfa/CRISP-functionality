from django.conf.urls import url,include
from rest_framework.routers import DefaultRouter
from .views import BatchViewSet,StudentViewSet


router = DefaultRouter()
router.register(r'batches', BatchViewSet, base_name='batch-viewset')
router.register(r'student', StudentViewSet, base_name='student-viewset')




urlpatterns = [
    url(r'^', include(router.urls)),

]
