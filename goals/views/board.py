from django.db import transaction
from rest_framework import (
    filters,
    permissions
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.pagination import LimitOffsetPagination

from goals.models import (
    Board,
    Goal
)
from goals.permissions import BoardPermissions
from goals.serializers import (
    BoardCreateSerializer,
    BoardListSerializer,
    BoardSerializer
)


class BoardCreateView(CreateAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer


class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
    permission_classes = [BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(
                category__board=instance
            ).update(
                status=Goal.Status.archived
            )
        return instance


class BoardListView(ListAPIView):
    model = Board
    permission_classes = [BoardPermissions]
    pagination_class = LimitOffsetPagination
    serializer_class = BoardListSerializer
    filter_backends = [
        filters.OrderingFilter,
    ]
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.filter(
            participants__user=self.request.user, is_deleted=False
        )
