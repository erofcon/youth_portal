from rest_framework import serializers
from django.utils.timezone import make_aware
from django.utils import timezone
from django.contrib.postgres.fields.ranges import DateTimeTZRange

from .models import RoomTag, Room, Booking
from apps.centers.serializers import YouthCenterSerializer
from apps.notifications.tasks import notify_responsible_of_new_booking


class RoomTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomTag
        fields = ["id", "name"]


class RoomSerializer(serializers.ModelSerializer):
    center = YouthCenterSerializer(read_only=True)
    tags = RoomTagSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = [
            "id", "name", "description", "image", "capacity",
            "tags", "center", "responsible_phone"
        ]


class BookingSerializer(serializers.ModelSerializer):
    start_datetime = serializers.DateTimeField(write_only=True)
    end_datetime = serializers.DateTimeField(write_only=True)

    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), source='room', write_only=True
    )

    start_at = serializers.DateTimeField(source='time_slot.lower',
                                         read_only=True)
    end_at = serializers.DateTimeField(source='time_slot.upper', read_only=True)

    status = serializers.CharField(read_only=True)
    rejection_reason = serializers.CharField(read_only=True, allow_blank=True)

    applicant_name = serializers.CharField(required=False, allow_blank=True)
    applicant_phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Booking
        fields = [
            "id", "room", "room_id", "start_datetime", "end_datetime", "status",
            "start_at", "end_at",
            "applicant_name", "applicant_phone", "applicant_telegram_username",
            "comment", "rejection_reason", "created_at",
        ]
        read_only_fields = ["created_at", "room", "start_at", "end_at"]

    # def validate(self, attrs):
    #     start = attrs.get("start_datetime")
    #     end = attrs.get("end_datetime")
    #     if end <= start:
    #         raise serializers.ValidationError(
    #             "Время окончания должно быть позже времени начала.")
    #
    #     user = self.context['request'].user
    #     if user and user.is_authenticated:
    #         attrs['applicant_name'] = user.get_full_name() or user.username
    #
    #         if hasattr(user, 'profile'):
    #             attrs['applicant_phone'] = user.profile.phone
    #             attrs['applicant_telegram_username'] = user.username.replace(
    #                 'tg_', '')
    #
    #     if not attrs.get('applicant_name') or not attrs.get('applicant_phone'):
    #         raise serializers.ValidationError(
    #             "Не удалось определить имя и телефон заявителя. "
    #             "Пожалуйста, укажите их в запросе или убедитесь, что пользователь аутентифицирован."
    #         )
    #
    #     return attrs

    def create(self, validated_data):
        start = validated_data.pop("start_datetime")
        end = validated_data.pop("end_datetime")
        user = self.context['request'].user

        if user.is_authenticated:
            validated_data['applicant'] = user

            validated_data[
                'applicant_name'] = user.get_full_name() or user.username
            
            if hasattr(user, 'profile'):
                validated_data['applicant_phone'] = user.profile.phone

        if timezone.is_naive(start):
            start = make_aware(start)
        if timezone.is_naive(end):
            end = make_aware(end)

        ts_range = DateTimeTZRange(lower=start, upper=end, bounds="[)")

        booking = Booking.objects.create(time_slot=ts_range, **validated_data)

        notify_responsible_of_new_booking.delay(booking.id)

        return booking


class RoomAvailabilitySerializer(serializers.Serializer):
    date = serializers.DateField()
    busy_slots = serializers.ListField(child=serializers.DictField())
