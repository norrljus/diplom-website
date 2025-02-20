from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from posts.views import PostsViewSet, LikeViewSet, CommentViewSet, TargetComment

router = DefaultRouter()
router.register('posts', PostsViewSet, basename='posts')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('posts/<int:post_id>/like/', LikeViewSet.as_view(), name="like"),
    path('posts/<int:post_id>/comment/', CommentViewSet.as_view(), name="comment"),
    path('posts/<int:post_id>/comment/<int:comm>', TargetComment.as_view(), name="tcomment"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
