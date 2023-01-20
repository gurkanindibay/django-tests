from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from tutorial.quickstart.serializers import UserSerializer, GroupSerializer,AccountSerializer
from .models import Account
from django_multitenant.utils import get_current_tenant
from django_multitenant.models import TenantModel
from typing import Dict, Generic, TypeVar

T = TypeVar("T")
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    print("UserViewSet executed")
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    
    print("GroupViewSet executed")
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class TenantModelViewSet(viewsets.ModelViewSet):
    model_class = TenantModel
    def get_queryset(self):
        return self.model_class.objects.all()
class AccountViewSet(TenantModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    model_class = Account
    serializer_class = AccountSerializer


    
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def account_list(request):
    """
    List all Accounts, or create a new account.
    """
    if request.method == 'GET':
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)