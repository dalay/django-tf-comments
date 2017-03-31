from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from comments.models import Comment
from comments.settings import COMMENTS_ON_PAGE


register = template.Library()

@register.inclusion_tag('comments/comments.html', takes_context=True)
def get_comments(context, obj):
    content_type=ContentType.objects.get_for_model(obj)

    comment_list = Comment.objects.filter(object_id=obj.pk, 
            content_type=content_type,
            status=True).select_related('parent', 'user')

    page = context['request'].GET.get('comments')
    paginator = Paginator(comment_list, COMMENTS_ON_PAGE)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        raise Http404
    return {
            'request': context['request'],
            "comments": comments,
            "object_id": obj.pk,
            'content_type': content_type
            }

# @register.inclusion_tag('comments/unpub_comments.html', takes_context=True)
# def get_unpublished_comments(context, items_on_page=20):
#     comment_list = Comment.objects.filter(status=False).select_related('parent',
#             'user', 'content_object')

#     paginator = Paginator(comment_list, items_on_page)
#     page = context['request'].GET.get('p')
#     try:
#         comments = paginator.page(page)
#     except PageNotAnInteger:
#         comments = paginator.page(1)
#     except EmptyPage:
#         raise Http404
#     return {"comments": comments }
    
# @register.inclusion_tag('comments/_comment.html')
# def get_comment(comment):
#     return { "comment": comment, }
