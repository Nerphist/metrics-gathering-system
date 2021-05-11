from django.urls import path

from documents.views import *

urlpatterns = [
    path('', DocumentListView.as_view(), name='Get all documents'),
    path('<int:document_id>/', DocumentRetrieveView.as_view(), name='Get document'),

    path('documentation/', DocumentationPartListView.as_view(), name='Get all documents'),
    path('documentation/<int:documentation_part_id>/', DocumentationPartRetrieveView.as_view(), name='Get document'),

    path('supply-contracts/', SupplyContractListView.as_view(), name='Get all supply contracts'),
    path('supply-contracts/<int:supply_contract_id>/', SupplyContractRetrieveView.as_view(),
         name='Get supply contract'),

    path('tariffs/', TariffListView.as_view(), name='Get all tariffs'),
    path('tariffs/<int:tariff_id>/', TariffRetrieveView.as_view(), name='Get tariff'),

]
