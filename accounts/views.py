from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from user.models import User
# Create your views here.

@api_view(["POST"])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if User.objects.filter(username=username).exit():

        return Response({
            "error": "Username already exit"
        },status=400)
    
    user = User.objects.create_user(
        username = username,
        password = password
    )
    return Response({
        "success" : True,
        "message" : "Account Created Successfully"
    })

@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        username = username,
        password = password
    )

    if user is None:
        return Response({
            "error": "Invalid Creditials"
        }, status=401)
    refresh = RefreshToken.for_user(user)

    return Response({
        "refresh"  : str(refresh),
        "access"   : str(refresh.access_token()),
        "username" : user.username
    })
    