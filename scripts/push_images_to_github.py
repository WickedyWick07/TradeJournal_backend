import os
from git import Repo

# Define paths
REPO_DIR = './TradeJournal_media'  # Path to your GitHub repository clone
IMAGE_DIR = os.path.join(REPO_DIR, 'journal_images')  # Images folder within the repo
BRANCH_NAME = 'master'
COMMIT_MESSAGE = 'Add new journal images'

# Function to get images to upload
def get_images_to_upload():
    return [f for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]

# Function to push images to GitHub
def push_images_to_github():
    # Initialize the repository
    try:
        repo = Repo(REPO_DIR)
        print(f"Loaded repository: {REPO_DIR}")
    except Exception as e:
        print(f"Failed to load repository: {e}")
        raise

    # Check if the repository is bare
    if repo.bare:
        raise Exception("The repository is bare. Please initialize it properly.")

    # Add images to the Git index
    images = get_images_to_upload()
    print(f"Found images to upload: {images}")

    if not images:
        print("No images to add. Exiting script.")
        return

    for image in images:
        image_path = os.path.join(IMAGE_DIR, image)
        repo.index.add([os.path.relpath(image_path, REPO_DIR)])
        print(f"Added {image} to Git index")

    # Commit changes
    repo.index.commit(COMMIT_MESSAGE)
    print(f"Committed changes: {COMMIT_MESSAGE}")

    # Push changes to GitHub
    origin = repo.remote(name='origin')
    try:
        origin.push(BRANCH_NAME)
        print(f"Pushed to branch {BRANCH_NAME} on remote")
    except Exception as e:
        print(f"Failed to push changes: {e}")
        raise

if __name__ == "__main__":
    try:
        push_images_to_github()
    except Exception as e:
        print(f"Script failed: {e}")
