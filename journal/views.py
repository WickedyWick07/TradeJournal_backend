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
import logging

logger = logging.getLogger('journal')


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

import os
from django.conf import settings
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_journal_entry(request):
    try:
        logger.info("Starting journal entry creation")
        logger.debug(f"Request data: {request.data}")

        # Log directory and file information
        logger.debug(f"Current Working Directory: {os.getcwd()}")
        logger.debug(f"BASE_DIR: {settings.BASE_DIR}")

        serializer = JournalEntrySerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save the journal entry
        journal_entry = serializer.save()

        # Process and save associated images
        images = request.FILES.getlist('images')
        logger.info(f"Number of images to process: {len(images)}")

        # Use MEDIA_ROOT to define the base directory for saving images
        image_dir = os.path.join(settings.MEDIA_ROOT, 'journal_images')
        os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists

        saved_images = []
        for image in images:
            try:
                image_serializer = JournalImageSerializer(
                    data={'image': image},
                    context={'request': request}
                )
                
                if not image_serializer.is_valid():
                    logger.error(f"Image validation failed: {image_serializer.errors}")
                    continue

                # Save the image and associate it with the journal entry
                journal_image = image_serializer.save(entry=journal_entry)
                saved_images.append(journal_image)

                # Save the file locally
                image_path = os.path.join(image_dir, image.name)
                with open(image_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
            
            except Exception as img_error:
                logger.exception(f"Error processing image: {img_error}")
                return Response(
                    {"error": "Failed to process an image", "details": str(img_error)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Asynchronous GitHub Push (Optional Enhancement)
        try:
            script_path = os.path.join(settings.BASE_DIR, 'scripts', 'push_images_to_github.py')
            
            # Use subprocess with more robust error handling
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=60  # 60-second timeout
            )

            # Log subprocess output
            if result.returncode == 0:
                logger.info("Successfully pushed images to GitHub")
                logger.debug(f"GitHub Push Output: {result.stdout}")
            else:
                logger.error(f"GitHub Push Failed: {result.stderr}")
                # You might want to implement retry logic or notification here

        except subprocess.TimeoutExpired:
            logger.error("GitHub push script timed out")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error running GitHub push script: {e}")

        return Response(
            {
                "message": "Journal entry and images created successfully", 
                "images_count": len(saved_images)
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        logger.exception("Unexpected error in journal entry creation")
        return Response(
            {"error": "Unexpected error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




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

