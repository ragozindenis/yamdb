from django_filters.rest_framework import (CharFilter, DjangoFilterBackend,
                                           FilterSet)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User

from .permissions import (IsAdmin, IsAdminModeratorAuthorOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenSerializer,
                          UserEditOwnProfileSerializer, UserSerializer)
from .utils import send_code_to_email


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserEditOwnProfileSerializer,
    )
    def me_get_and_edit(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response('method wrong', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_and_send_confirmation_code(request):
    username = request.data.get('username')
    if not User.objects.filter(username=username).exists():
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        me = ('me', 'ME', 'Me', 'mE')
        if serializer.validated_data['username'] not in me:
            serializer.save()
            send_code_to_email(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            'username wrong',
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = get_object_or_404(User, username=username)
    serializer = SignUpSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    if serializer.validated_data['email'] == user.email:
        serializer.save()
        send_code_to_email(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response('email wrong', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_tokens_for_user(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data['username']
    )
    if (
        serializer.validated_data['confirmation_code']
        == user.confirmation_code
    ):
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'})
    return Response(
        {'message': 'confirmation_code wrong'},
        status=status.HTTP_400_BAD_REQUEST,
    )


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def retrieve(self, request, slug=None):
        return Response(
            {'message': 'Метод GET недоступен для этого эндпойнта'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def retrieve(self, request, slug=None):
        return Response(
            {'message': 'Метод GET недоступен для этого эндпойнта'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class TitleFilter(FilterSet):
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ['name', 'year', ]


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
