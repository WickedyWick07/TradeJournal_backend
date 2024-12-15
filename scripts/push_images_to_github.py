import os
import shutil
from git import Repo
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Define paths
DJANGO_MEDIA_PATH = r'C:\Users\Mashaba Media\Desktop\TradeJournal\AiJournal\media\journal_images'
GITHUB_REPO_PATH = r'C:\Users\Mashaba Media\Desktop\TradeJournal\AiJournal\scripts\TradeJournal_media'
BRANCH_NAME = 'master'

def sync_images():
    """
    Synchronize images from Django media folder to GitHub repository folder
    """
    try:
        # Ensure destination directory exists
        journal_images_path = os.path.join(GITHUB_REPO_PATH, 'journal_images')
        os.makedirs(journal_images_path, exist_ok=True)

        # Get list of files in source and destination
        source_files = set(os.listdir(DJANGO_MEDIA_PATH))
        dest_files = set(os.listdir(journal_images_path))

        # Copy new files
        new_files = source_files - dest_files
        for file in new_files:
            src_path = os.path.join(DJANGO_MEDIA_PATH, file)
            dst_path = os.path.join(journal_images_path, file)
            shutil.copy2(src_path, dst_path)
            logging.info(f'Copied new image: {file}')

        return new_files  # Return new files for Git tracking
    except Exception as e:
        logging.error(f'Error synchronizing images: {e}')
        return set()

def push_images_to_github():
    """
    Commit and push new images to GitHub repository
    """
    try:
        # Open the repository
        repo = Repo(GITHUB_REPO_PATH)

        # Sync images and get new files
        new_files = sync_images()

        if new_files:
            # Stage changes
            repo.git.add('.')

            # Create commit with timestamp
            commit_message = f'Add journal images - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            repo.index.commit(commit_message)

            # Push to remote
            origin = repo.remote(name='origin')
            origin.push()

            logging.info(f'Successfully pushed {len(new_files)} new images to GitHub')
        else:
            logging.info('No new images to push')

    except Exception as e:
        logging.error(f'GitHub push failed: {e}')
        raise

def main():
    try:
        push_images_to_github()
    except Exception as e:
        logging.error(f"Script failed: {e}")

if __name__ == "__main__":
    main()