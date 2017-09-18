from django import template
from django.utils import formats
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from comments.models import Comment
from comments.settings import COMMENTS_ON_PAGE


register = template.Library()

# def last_comment(obj):
#     ct = ContentType.objects.get_for_model(obj)
#     return Comment.objects.filter(content_type=ct).last()


@register.simple_tag
def comments_count(obj):
    return Comment.cached.object_comments_count(obj)

@register.inclusion_tag('comments/latest_commetns.html')
def latest_comments(limit=5):
    comments = Comment.objects.filter(status=1).order_by('-created')[:limit]
    return {'comments': comments}

@register.inclusion_tag('comments/comments.html', takes_context=True)
def get_comments(context, obj, order_by='desc'):
    '''
    Возращает комментарии для указанного объекта.

    Сортировка по-умолчанию - по нисходящей. Если нужно иначе, то
    следует в шаблоне передать для  переменной order_by значение 'asc'.
    '''
    content_type = ContentType.objects.get_for_model(obj)

    comment_list = Comment.objects.filter(object_id=obj.pk,
                                          content_type=content_type,
                                          status=True).select_related('parent', 'user')

    if order_by == 'asc':
        comment_list = comment_list.order_by('created')

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


@register.simple_tag
def last_comment_datetime(obj):
    ct = ContentType.objects.get_for_model(obj)
    qs = Comment.objects.filter(object_id=obj.pk,
                                content_type=ct)
    if qs.exists():
        return formats.date_format(qs.latest('created').created, "SHORT_DATETIME_FORMAT")
    return 'тишина'

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
