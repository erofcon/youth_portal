from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DistrictViewSet, YouthCenterViewSet

router = DefaultRouter()
router.register("districts", DistrictViewSet, basename="districts")
router.register("centers", YouthCenterViewSet, basename="centers")

urlpatterns = [
    path("", include(router.urls)),
]
