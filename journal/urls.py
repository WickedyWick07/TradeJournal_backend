from django.urls import path
from.views import fetch_all_entries, create_journal_entry, delete_journal_entry, update_journal_entry, fetch_entries_by_account, fetch_journal_entry, fetch_trading_journals

urlpatterns = [
    path('create-journal-entry/', create_journal_entry, name='create-journal-entry'),
    path('fetch-journal-entry/<int:id>/', fetch_journal_entry, name='fetch-journal-entry'),
    path('fetch-all-journal-entries/', fetch_all_entries, name='fetch-all-entries'),
    path('delete-journal-entry/<int:id>/', delete_journal_entry, name='delete-journal-entry'),
    path('update-journal-entry/<int:id>/', update_journal_entry, name='update-journal-entry'),
    path('fetch-trading-journals/', fetch_trading_journals, name='fetch-trading-journals'),
    path('journal-entries/', fetch_entries_by_account, name='fetch-entries-by-account'),
]
