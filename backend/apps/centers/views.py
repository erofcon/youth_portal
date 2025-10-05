from rest_framework import viewsets, mixins
from .models import District, YouthCenter
from .serializers import DistrictSerializer, YouthCenterSerializer


class DistrictViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class YouthCenterViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = YouthCenter.objects.select_related("district")
    serializer_class = YouthCenterSerializer
