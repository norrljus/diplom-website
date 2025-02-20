from rest_framework import serializers
from posts.models import Post, Comment, PostLikes
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


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLikes
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        if data.get('author') == self.context["request"].user:
            raise serializers.ValidationError('Logged in User is not an Author')
        return data

    def get_likes_count(self, obj):
        return obj.postlikes_set.count()




