from django.contrib import admin
from comments.models import Comment


# Делаем возможность снимами с публикации и публиковать комменты.
def make_published(modeladmin, request, queryset):
        queryset.update(status=True)

def make_unpublished(modeladmin, request, queryset):
        queryset.update(status=False)

make_published.short_description = "Опубликовать"
make_unpublished.short_description = "Снять с публикации"


class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_comment_text', 'content_object', 'created', 'status')
    list_filter = ('status',)
    actions = [make_published, make_unpublished]

admin.site.register(Comment, CommentAdmin)
