from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import FAQ, Post
from .serializers import FAQSerializer, PostSerializer
from .services import PostService
from apps.core.pagination import paginated_response


class KontenViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], url_path='posts')
    def posts(self, request):
        queryset = PostService.get_published_posts()
        return paginated_response(request, queryset, PostSerializer)

    @action(detail=True, methods=['get'], url_path='posts')
    def post_detail(self, request, pk=None):
        post = Post.objects.filter(slug=pk).first()
        if not post:
            return Response(status=404)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='faqs')
    def faqs(self, request):
        # `FAQ.aktif` was removed; return all FAQs instead.
        queryset = FAQ.objects.all()
        return paginated_response(request, queryset, FAQSerializer)