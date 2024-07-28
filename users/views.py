from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from users.models import User
from users.permissions import IsUserProfile
from users.serializers import AuthUserSerializer, UserSerializer


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsUserProfile]
        if self.action in ['create']:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        password = request.data.get('password')
        user = User.objects.get(email=serializer.data.get('email'))
        user.set_password(password)
        user.save()
        return Response(serializer.data, status=201, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        if self.request.user == self.get_object() or self.request.user.is_superuser:
            serializer_class = UserSerializer
        else:
            serializer_class = AuthUserSerializer
        serializer = serializer_class(self.get_object())
        serializer_data = serializer.data

        return Response(serializer_data)