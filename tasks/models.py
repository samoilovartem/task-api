from django.conf import settings
from django.db import models


class Task(models.Model):
    """A task belonging to a user.

    Attributes:
        title: Short title of the task.
        description: Detailed description (optional).
        status: Completion status, False by default.
        created_at: Timestamp of creation (auto-set).
        user: The owner of the task.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
