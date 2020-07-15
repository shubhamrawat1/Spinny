from rest_framework import serializers
from test_task.models import Box

# Serializer for Update Create and List
class BoxCreateSerializer(serializers.ModelSerializer):
    # created_by = serializers.SerializerMethodField()

    class Meta:
        model = Box
        fields = [
            'id',
            'length',
            'width',
            'height',
        ]


class BoxListSerializerUser(serializers.ModelSerializer):
    # created_by = serializers.SerializerMethodField()

    class Meta:
        model = Box
        fields = [
            'id',
            'length',
            'width',
            'height',
            'area',
            'volume',
        ]


class BoxSerializer(serializers.ModelSerializer):
    # created_by = serializers.SerializerMethodField()

    class Meta:
        model = Box
        fields = '__all__'

    # def get_created_by(self, instance):
    #     request = self.context.get('request')
    #     instance.created_by = request.user
    #     instance.save()