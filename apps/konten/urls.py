from django.urls import path

from .views import KontenViewSet

posts_list = KontenViewSet.as_view({'get': 'posts'})
post_detail = KontenViewSet.as_view({'get': 'post_detail'})
faqs = KontenViewSet.as_view({'get': 'faqs'})

urlpatterns = [
	path('posts/', posts_list, name='posts-list'),
	path('posts/<slug:pk>/', post_detail, name='posts-detail'),
	path('faq/', faqs, name='faq-list'),
]
