from django.urls import path
from .views import fetch_account, create_account, fetch_accounts  # Ensure the correct import path

urlpatterns = [
    path('create-account/', create_account, name='create_account'),  # Add trailing slash for consistency
    path('fetch-account/<int:id>/', fetch_account, name='fetch_account'),  # Corrected typo and added trailing slash
    path('fetch-accounts/', fetch_accounts, name='fetch_accounts'),  # Corrected typo and added trailing slash
]
