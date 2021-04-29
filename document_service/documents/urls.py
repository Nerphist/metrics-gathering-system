from django.urls import path

from documents.views import *

urlpatterns = [
    path('', DocumentListView.as_view(), name='Get all documents'),
    path('<int:document_id>/', DocumentRetrieveView.as_view(), name='Get document'),

]
