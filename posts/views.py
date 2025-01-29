from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .filters import PostFilter
from .models import Post, Images, PostLikes, User, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly


class PostsViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly|IsAdminUser]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PostFilter

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            return [IsAuthenticated()]
        elif self.action == "delete":
            return [IsOwnerOrReadOnly()]
        return []


class NewPost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")
        post_id = Post.objects.create(author_id=request.user.id ,text=text)
        images = request.FILES.getlist('images')
        for image in images:
            Images.objects.create(image=image, post_id=post_id)
        return Response({"message": "Успешно"})


class LikeViewSet(APIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        user = User.objects.filter(id=request.user.id).first()
        like, created = PostLikes.objects.get_or_create(user_id=user, post_id=post)
        if not created:
            like.delete()
            return Response({"message": "Лайк удален"})
        return Response({"message": "Лайк поставлен"})


class CommentViewSet(APIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        text = request.data.get("text")
        user = User.objects.filter(id=request.user.id).first()
        Comment.objects.create(post=post, text=text, author=user)
        return Response({"message": "Комментарий создан"})


class TargetComment(APIView):
    serializer_class = CommentSerializer

    def patch(self, request, post_id, comm):
        try:
            post = Post.objects.filter(id=post_id).first()
            comment = Comment.objects.filter(post=post, id=comm).first()
        except Comment.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(comment, data=request.data, partial=True)
        self.check_object_permissions(request, comment)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, comm):
        try:
            post = Post.objects.filter(id=post_id).first()
            comment = Comment.objects.filter(post=post, id=comm).first()
        except Comment.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, comment)
        try:
            comment.delete()
        except AttributeError:
            return Response({"message": "Комментарий не найден"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Комментарий удален"}, status=status.HTTP_204_NO_CONTENT)

