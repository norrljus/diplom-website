from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(max_length=165)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} posts "{self.text}"'


class Images(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images/')
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post_id.id} - "{self.image}"'


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=165)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} comments "{self.text}" to {self.post.text}'


class PostLikes(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user_id} likes "{self.post_id.text}"'
