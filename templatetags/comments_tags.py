from django import template
from django.utils import formats
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from comments.models import Comment
from comments.settings import COMMENTS_ON_PAGE


register = template.Library()


@register.simple_tag
def comments_count(obj):
    '''
    Подсчет колличества комментов для конкретного объекта.
    '''
    return Comment.cached.object_comments_count(obj)


@register.inclusion_tag('comments/latest_comments.html')
def latest_comments(limit=5, model=None):
    '''
    Получаем последние комменты со статусом True.
    '''
    qs = Comment.objects.filter(status=True).order_by('-created')
    # Если "пришла" модель, то получаем последние комменты для
    # инстансов только этой модели.
    if model:
        ct = ContentType.get_for_model(model)
        qs.filter(content_type=ct)
    if limit > 0:
        comments = qs[:limit]
        return {'comments': comments}


@register.inclusion_tag('comments/comments.html', takes_context=True)
def get_comments(context, obj, order_by_desc=True):
    '''
    Возращает комментарии для указанного объекта.

    Сортировка по-умолчанию - по нисходящей. Если нужно иначе, то
    следует в шаблоне передать для  переменной order_by_desc значение "False".
    Сортировка по-умолчанию - сначала новые (DESC).
    '''
    content_type = ContentType.objects.get_for_model(obj)

    comment_list = Comment.objects.filter(object_id=obj.pk,
                                          content_type=content_type,
                                          status=True).select_related('parent', 'user')

    if not order_by_desc:
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
