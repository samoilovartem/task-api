from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from tasks.models import Task
from tasks.serializers import TaskSerializer


class TaskViewSet(ModelViewSet):
    """ViewSet for managing user tasks.

    Provides list, create, retrieve, update, and delete actions.
    Each user can only access their own tasks.
    Supports filtering by status via query parameter `?status=true/false`.
    """

    queryset = Task.objects.none()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        """Return tasks belonging to the authenticated user."""
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Assign the authenticated user as the task owner on creation."""
        serializer.save(user=self.request.user)
