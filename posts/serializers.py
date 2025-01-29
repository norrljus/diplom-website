from rest_framework import serializers
from posts.models import Post, Comment, Images, PostLikes
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'created_at']

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        if data.get('author') == self.context["request"].user:
            raise serializers.ValidationError('Logged in User is not an Author')
        return data


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ('image',)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLikes
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, source='images_set')
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')
    likes_count = serializers.SerializerMethodField()


    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'images', 'created_at', "likes_count", 'comments']

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        if data.get('author') == self.context["request"].user:
            raise serializers.ValidationError('Logged in User is not an Author')
        return data

    def get_likes_count(self, obj):
        return obj.postlikes_set.count()




