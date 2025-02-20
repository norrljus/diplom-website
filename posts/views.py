from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .filters import PostFilter
from .models import Post, PostLikes, User, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly


class PostsViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly|IsAdminUser]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PostFilter
    parser_classes = [JSONParser, MultiPartParser, FileUploadParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            return [IsAuthenticated()]
        elif self.action == "delete":
            return [IsOwnerOrReadOnly()]
        return []



class LikeViewSet(APIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        user = User.objects.filter(id=request.user.id).first()
        like, created = PostLikes.objects.get_or_create(user_id=user, post_id=post)
        if not created:
            like.delete()
            return Response({"message": "Лайк удален"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "Лайк поставлен"}, status=status.HTTP_201_CREATED)


class CommentViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.filter(id=post_id).first()
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(data=request.data, context={"request": request}, partial=True)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response({"message": "Комментарий создан"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TargetComment(APIView):
    serializer_class = CommentSerializer

    def patch(self, request, post_id, comm):
        try:
            post = Post.objects.filter(id=post_id).first()
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            comment = Comment.objects.filter(post=post, id=comm).first()
        except Comment.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(comment, data=request.data, context={"request": request}, partial=True)
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

