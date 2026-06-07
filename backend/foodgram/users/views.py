from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User, Subscription
from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    SubscriptionSerializer,
    SetPasswordSerializer,
    SetAvatarSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """Представления пользователя.

    Описывает список, профиль, подписки, аватар, пароль.
    """

    queryset = User.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от выполняемого действия.

        Для действия 'create' выбирает CustomUserCreateSerializer,
        для остальных действий выбирает CustomUserSerializer.
        Возвращает сериализатор для текущего действия.
        """
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    def get_permissions(self):
        """Выбирает права доступа в зависимости от выполняемого действия.

        Для действия 'create' выбирает AllowAny, для действий 'me,
        subscriptions, subscribe, set_password, avatar' выбирает
        IsAuthenticated. Для всех остальных действий выбирает - AllowAny.
        """
        if self.action == 'create':
            self.permission_classes = (permissions.AllowAny,)
        elif self.action in (
            'me',
            'subscriptions',
            'subscribe',
            'set_password',
            'avatar'
        ):
            self.permission_classes = (permissions.IsAuthenticated,)
        else:
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        """Возвращает пагинированный ответ со списком подписок пользователя."""
        authors = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, id=None):
        """ Управление подписками: создание и удаление.

        POST: подписаться на автора.
        DELETE: отписаться от автора.
        """
        author = self.get_object()
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            _, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if not created:
                return Response(
                    {'errors': 'Уже подписан.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        subscription = get_object_or_404(
            Subscription,
            user=request.user,
            author=author,
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def me(self, request):
        """Возвращает профиль текущего пользователя."""
        serializer = CustomUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        """Выполняет валидацию нового пароля."""
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['PUT', 'DELETE'])
    def avatar(self, request):
        """Обрабатывает обвноление и удаления аватара пользователя."""
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(
                request.user,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        request.user.avatar.delete()
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
