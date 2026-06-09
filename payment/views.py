from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework.decorators import api_view
# Create your views here.

# --> IPN mimickry <--

@api_view(["POST"])
def pesapal_ipn(request):
    print("IPN HIT", request.data)
    return Response({
        "message" : "IPN received"
    })