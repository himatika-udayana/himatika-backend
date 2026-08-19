from rest_framework.pagination import PageNumberPagination


def paginated_response(request, queryset, serializer_class):
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(page, many=True)
    return paginator.get_paginated_response(serializer.data)
