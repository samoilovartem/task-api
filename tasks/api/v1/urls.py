from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tasks.api.v1.tasks import TaskViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
