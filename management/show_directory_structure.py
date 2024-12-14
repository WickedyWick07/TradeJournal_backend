# In your Django app, create a file: management/commands/show_directory_structure.py
from django.core.management.base import BaseCommand
import os
import django
from django.conf import settings

class Command(BaseCommand):
    help = 'Prints the directory structure of the project'

    def handle(self, *args, **options):
        # Print current working directory
        self.stdout.write(self.style.SUCCESS(f"Current Working Directory: {os.getcwd()}"))
        
        # Print BASE_DIR
        self.stdout.write(self.style.SUCCESS(f"BASE_DIR: {settings.BASE_DIR}"))

        # Recursively list directories and files
        def print_directory_structure(startpath):
            for root, dirs, files in os.walk(startpath):
                level = root.replace(startpath, '').count(os.sep)
                indent = ' ' * 4 * level
                self.stdout.write(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 4 * (level + 1)
                for f in files:
                    self.stdout.write(f"{subindent}{f}")

        # Print directory structure
        print_directory_structure(settings.BASE_DIR)