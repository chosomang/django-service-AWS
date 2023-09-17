from django.shortcuts import render
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response

API_VERSION = 'v1'
# api index
@login_required
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
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter

class CypherListCreateView(generics.ListCreateAPIView):
    queryset = Cypher.objects.all()
    serializer_class = CypherSerializer
    

class CypherViewSet(viewsets.ModelViewSet):
    queryset = Cypher.objects.all()
    serializer_class = CypherSerializer
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['cypher_type']
    ordering_fields = ['index']
    
    def get_queryset(self):
        queryset = Cypher.objects.all()
        cypher_type = self.request.query_params.get('cypher_type', None)
        
        # filtering
        if cypher_type:
            queryset = queryset.filter(title__icontains=cypher_type)
        
        # ordering
        ordering = self.request.query_params.get('ordering', None)
        if ordering in self.ordering_fields:
            queryset = queryset.order_by(ordering)
        
        return queryset


@api_view(['POST'])
def create_cypher(request):
    serializer = CypherSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
