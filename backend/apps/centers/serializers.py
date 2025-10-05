from rest_framework import serializers
from .models import District, YouthCenter


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "name"]


class YouthCenterSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = YouthCenter
        fields = [
            "id", "name", "district", "emblem", "address", "phone",
            "responsible_name", "responsible_phone"
        ]
