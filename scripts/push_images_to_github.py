import os
import subprocess
from git import Repo

# Define paths
IMAGE_DIR = 'AiJournal/media/journal_images'
REPO_DIR = './TradeJournal_media'  # Relative path to the cloned GitHub repository
GITHUB_USERNAME = 'WickedyWick07'
GITHUB_REPO = 'https://github.com/WickedyWick07/TradeJournal_media.git'
BRANCH_NAME = 'master'  # or whichever branch you want to push to

# Path to the images in your repository
def get_images_to_upload():
    return [f for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]

# Function to add, commit, and push images to GitHub
def push_images_to_github():
    # Initialize repo
    repo = Repo(REPO_DIR)
    assert not repo.bare

    # Add images to Git repo
    images = get_images_to_upload()
    for image in images:
        image_path = os.path.join(IMAGE_DIR, image)
        repo.index.add([image_path])
    
    # Commit and push to GitHub
    commit_message = 'Add new journal images'
    repo.index.commit(commit_message)
    origin = repo.remote(name='origin')
    origin.push(BRANCH_NAME)
    print(f'Images pushed to GitHub repo {GITHUB_REPO} on branch {BRANCH_NAME}')

if __name__ == "__main__":
    push_images_to_github()
