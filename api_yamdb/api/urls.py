from django.urls import include, path
from rest_framework import routers

from .custom_routers import PutMthodNotAllow
from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet,
                    get_tokens_for_user, signup_and_send_confirmation_code)

router_no_put = PutMthodNotAllow()
router_v1 = routers.DefaultRouter()
router_no_put.register('users', UserViewSet, basename='user')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include(router_no_put.urls)),
    path('v1/auth/signup/', signup_and_send_confirmation_code),
    path('v1/auth/token/', get_tokens_for_user),
]
