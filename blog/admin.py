from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Post admin view"""
    raw_id_fields=['likes', 'tags']

admin.site.register(Tag)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comment admin view"""
    raw_id_fields = ['post', 'author']
    list_select_related = ['post', 'author']
