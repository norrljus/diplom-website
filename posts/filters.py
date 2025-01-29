from django_filters import rest_framework as filters
from django_filters.rest_framework import DateFromToRangeFilter

from .models import Post


class PostFilter(filters.FilterSet):

    created_at = DateFromToRangeFilter()

    class Meta:
        model = Post
        fields = ['created_at', 'author']