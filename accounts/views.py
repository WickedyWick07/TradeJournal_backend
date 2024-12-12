from rest_framework import status 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import TradingAccount
from .serializers import TradingAccountSerializers
from journal.models import AccountJournal
from journal.models import JournalEntry


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_account(request):
    serializer = TradingAccountSerializers(data=request.data, context = {'request': request})
    
    if serializer.is_valid():
        # Assign the authenticated user to the account
        serializer.save(user=request.user)
        return Response({'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)
    else: 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_accounts(request):
    accounts = TradingAccount.objects.filter(user=request.user)
    serializer = TradingAccountSerializers(accounts, many=True)
 
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_account(request, id):
    # Ensure the account belongs to the authenticated user
    account = get_object_or_404(TradingAccount, pk=id, user=request.user)
    serializer = TradingAccountSerializers(account)

    return Response(serializer.data, status=status.HTTP_200_OK)


 


