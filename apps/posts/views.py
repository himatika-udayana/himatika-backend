from rest_framework import generics, permissions

from apps.konten.models import Post
from .serializers import PostSerializer
from apps.konten.services import PostService


class PostListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = PostService.get_published_posts()
    serializer_class = PostSerializer


class PostDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
