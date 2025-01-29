from django.contrib import admin
from .models import Post, Comment, Images, PostLikes

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Images)
admin.site.register(PostLikes)