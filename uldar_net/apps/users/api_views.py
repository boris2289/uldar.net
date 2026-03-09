# Python imports
from typing import Any

from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer, ListUserSerializer
from rest_framework import generics
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request as DRFRequest
from rest_framework_simplejwt.authentication import JWTAuthentication


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer # add it
    permission_classes = [AllowAny]

class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        if not user.check_password(serializer.validated_data.get("old_password")):
            return Response(
                {"old_password": ["Wrong password."]}, 
                status=HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data.get("new_password"))
        user.save()

        return Response({"status": "password changed"}, status=HTTP_200_OK)
    
class ListUserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = [AllowAny]

class RetrieveUserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = [AllowAny]
