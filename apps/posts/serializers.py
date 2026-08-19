from apps.konten.serializers import PostSerializer as KontenPostSerializer


class PostSerializer(KontenPostSerializer):
    """Thin wrapper around the existing Konten PostSerializer.

    This keeps a separate module for posts while reusing the shared
    serialization logic in `apps.konten.serializers`.
    """
    pass
