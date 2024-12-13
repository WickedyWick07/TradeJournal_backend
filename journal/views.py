from rest_framework import status 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import JournalEntry, AccountJournal, JournalImage
from .serializers import JournalEntrySerializer, AccountJournalSerializer, JournalImageSerializer
from django.conf import settings 
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from rest_framework.pagination import PageNumberPagination
import requests

def upload_image_to_netlify(image):
    # URL of your Netlify function that handles the image upload
    netlify_function_url = 'https://radiant-cocada-ffd780.netlify.app/.netlify/functions/uploadImage'
    
    # Prepare the files data for the POST request
    files = {
        'file': (image.name, image, image.content_type)
    }

    # Send a POST request to the Netlify function to upload the image
    response = requests.post(netlify_function_url, files=files)

    # If the upload was successful, the response should contain the URL of the uploaded image
    if response.status_code == 200:
        return response.json().get('image_url')
    else:
        return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_journal_entry(request):
    # Validate the journal entry data
    serializer = JournalEntrySerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Save the journal entry
        journal_entry = serializer.save()

        # Get the list of images from the request
        images = request.FILES.getlist('images')
        
        for image in images:
            # Send the image to the Netlify function for uploading
            image_url = upload_image_to_netlify(image)
            
            if image_url:
                # Save the image URL in the JournalImage model
                JournalImage.objects.create(entry=journal_entry, image_url=image_url)
            else:
                return Response({'error': 'Failed to upload image to Netlify'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response('Entry created successfully', status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_all_entries(request):
    
    entries = JournalEntry.objects.filter(user=request.user)
    serializer = JournalEntrySerializer(entries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_journal_entry(request, id):
    entry = get_object_or_404(JournalEntry, pk=id, user=request.user)
    serializer = JournalEntrySerializer(entry)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_entries_by_account(request):
    paginator = PageNumberPagination()
    paginator.page_size = 10

    # Get the account_id from the query parameters
    account_id = request.query_params.get('account_id')

    if account_id:
        # Filter journal entries by account if provided
        entries = JournalEntry.objects.filter(user=request.user, journal__account__id=account_id)
    else:
        # If no account_id is provided, return all entries for the user
        entries = JournalEntry.objects.filter(user=request.user)

    # Paginate the results
    result_page = paginator.paginate_queryset(entries, request)
    serializer = JournalEntrySerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_journal_entry(request, id):
    entry = get_object_or_404(JournalEntry, pk=id , user=request.user)

    entry.delete()
    return Response({'message': 'Entry deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_journal_entry(request, id):
    entry = get_object_or_404(JournalEntry, pk=id, user=request.user)
    serializer = JournalEntrySerializer(entry, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response('Entry updated successfully', status=status.HTTP_200_OK)
    else: 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_trading_journals(request):
    journals = AccountJournal.objects.filter(user=request.user)
    serializer = AccountJournalSerializer(journals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

