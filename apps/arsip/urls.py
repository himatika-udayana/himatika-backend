from django.urls import path

from .views import ArsipViewSet

arsip_list = ArsipViewSet.as_view({'get': 'arsip_list'})
arsip_detail = ArsipViewSet.as_view({'get': 'arsip_detail'})
arsip_download = ArsipViewSet.as_view({'get': 'download'})

urlpatterns = [
	path('', arsip_list, name='arsip-list'),
	path('<int:pk>/', arsip_detail, name='arsip-detail'),
	path('<int:pk>/download/', arsip_download, name='arsip-download'),
]
