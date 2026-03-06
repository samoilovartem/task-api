from django.contrib.auth import get_user_model
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from tasks.models import Task

User = get_user_model()


class TaskSerializer(ModelSerializer):
    """Serializer for Task model.

    Handles serialization/deserialization of tasks.
    Fields `id` and `created_at` are read-only.
    """

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(ModelSerializer):
    """Serializer for user registration.

    Accepts username and password (min 8 chars).
    Password is write-only and the user is created via `create_user`.
    """

    password = CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a new user with a hashed password."""
        return User.objects.create_user(**validated_data)
