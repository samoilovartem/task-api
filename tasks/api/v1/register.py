from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from tasks.serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    """Create a new user account.

    Accepts username and password, returns the created user's id and username.
    No authentication required.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
