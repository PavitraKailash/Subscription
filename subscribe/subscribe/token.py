from django.contrib.auth.models import User
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    def get_token(cls, user):
        token = super(UserSerializer, cls).get_token(user)
        # Add custom claims
        token['username'] = user.username
        return token


class UserAPIView(RetrieveAPIView):
    serializer_class = UserSerializer