from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CypherSerializer

API_VERSION = 'v1'
# api index
def index(request):
    return render(request, "api/index.html")

def version(request):
    return render(request, "api/v1.html")

def cypher(request):
    if request.method == 'POST':
        cypher = request.POST.get('cypher', '')
        return render(request, 'api/{}/cypher.html'.format(API_VERSION), {'cypher': cypher})
    else: # GET
        return render(request, 'api/{}/cypher.html'.format(API_VERSION))

from rest_framework import generics
from rest_framework import viewsets
from .models import Cypher
from .serializers import CypherSerializer

class CypherListCreateView(generics.ListCreateAPIView):
    queryset = Cypher.objects.all()
    serializer_class = CypherSerializer
    

class CypherViewSet(viewsets.ModelViewSet):
    queryset = Cypher.objects.all()
    serializer_class = CypherSerializer


@api_view(['POST'])
def create_cypher(request):
    serializer = CypherSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
