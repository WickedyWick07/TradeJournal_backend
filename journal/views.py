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
from supabase import create_client, Client
import uuid
import os


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_journal_entry(request):
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)

    serializer = JournalEntrySerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        journal_entry = serializer.save()
        
        # Handle image uploads
        images = request.FILES.getlist('images')
        image_urls = []

        for image in images:
            # Generate a unique filename
            file_extension = os.path.splitext(image.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            try:
                # Upload to Supabase Storage
                supabase.storage.from_('trade-images').upload(
                    path=unique_filename, 
                    file=image.read(),
                    file_options={"content-type": image.content_type}
                )

                # Get public URL
                public_url = supabase.storage.from_('trade-images').get_public_url(unique_filename)
                
                # Create JournalImage record with Supabase URL
                JournalImage.objects.create(
                    entry=journal_entry, 
                    image_url=public_url
                )
                
                image_urls.append(public_url)

            except Exception as e:
                # Log the error, but continue processing other images
                print(f"Image upload error: {e}")

        return Response({
            'message': 'Entry created successfully', 
            'image_urls': image_urls
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for creating a journal entry
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

