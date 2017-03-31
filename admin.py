from django.contrib import admin
from comments.models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_comment_text', 'content_object', 'created', 'status')

admin.site.register(Comment, CommentAdmin)
