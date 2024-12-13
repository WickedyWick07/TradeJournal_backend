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
import os
import subprocess
from git import Repo


# Define paths for your local repository and images directory
IMAGE_DIR = os.path.join(os.getcwd(), 'AiJournal/media/journal_images')  # Path to the images folder
REPO_DIR = os.path.join(os.getcwd(), 'TradeJournal_media')  # Your local GitHub repo directory

# Function to get images to upload (in case you need them after the journal entry creation)
def get_images_to_upload():
    return [f for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]

# Function to push images to GitHub
def push_images_to_github():
    repo = Repo(REPO_DIR)
    assert not repo.bare

    # Get images and add to Git
    images = get_images_to_upload()
    for image in images:
        image_path = os.path.join(IMAGE_DIR, image)
        repo.index.add([image_path])

    # Commit and push to GitHub
    commit_message = 'Add new journal images'
    repo.index.commit(commit_message)
    origin = repo.remote(name='origin')
    origin.push('master')  # Replace 'master' with your branch if needed
    print(f'Images pushed to GitHub repo on branch master')

# API View to create the journal entry
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_journal_entry(request):
    serializer = JournalEntrySerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        # Save the journal entry first
        journal_entry = serializer.save()

        # Get the uploaded images
        images = request.FILES.getlist('images')
        
        # Save images to your local folder temporarily and associate with the journal entry
        for image in images:
            image_path = os.path.join(IMAGE_DIR, image.name)
            
            # Save the image temporarily
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # Create JournalImage instance and associate with the journal entry
            JournalImage.objects.create(entry=journal_entry, image=image)
        
        # Call the function to push images to GitHub after saving them
        subprocess.run(['python3', 'AiJournal/scripts/push_images_to_github.py'])

        return Response('Entry created and images pushed successfully', status=status.HTTP_201_CREATED)
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

