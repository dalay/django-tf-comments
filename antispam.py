from django.core.cache import cache
from functools import wraps
from django.conf import settings as django_settings
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils import six
from django.utils.decorators import available_attrs
from django.http import JsonResponse
from . import settings


def antispam_equals(val):
    """
        Default verifier used if COMMENTS_ANTISPAM_VERIFIER is not specified.
        Ensures val == COMMENTS_ANTISPAM_VALUE or COMMENTS_ANTISPAM_VALUE() if it's a callable.
    """
    expected = settings.COMMENTS_ANTISPAM_VALUE
    if callable(expected):
        expected = expected()
    return val == expected


def verify_antispam_value(request, field_name):
    """
        Verify that request.POST[field_name] is a valid antispam.

        Ensures that the field exists and passes verification according to
        COMMENTS_ANTISPAM_VERIFIER.
    """
    ip = request.META['REMOTE_ADDR']
    print(ip)
    field = field_name or settings.COMMENTS_ANTISPAM_FIELD_NAME
    resp = render_to_string('comments/comments_antispam_error.html',
                            {'fieldname': field})
    resp_ajax = render_to_string('comments/comments_antispam_error_ajax.html',
                                 {'fieldname': field})
    if check_spam_ip(ip):
        if request.is_ajax():
            return JsonResponse({'__all__': resp_ajax, }, status=403)
        return HttpResponseBadRequest(resp)

    verifier = getattr(
        django_settings, 'COMMENTS_ANTISPAM_VERIFIER', antispam_equals)
    if request.method == 'POST':
        if field not in request.POST or not verifier(request.POST[field]):
            set_spam_ip(ip)
            if request.is_ajax():
                return JsonResponse({'__all__': resp_ajax, }, status=403)
            return HttpResponseBadRequest(resp)


def check_antispam(func=None, field_name=None):
    """
        Check request.POST for valid antispam field.

        Takes an optional field_name that defaults to COMMENTS_ANTISPAM_FIELD_NAME if
        not specified.
    """
    # hack to reverse arguments if called with str param
    if isinstance(func, six.string_types):
        func, field_name = field_name, func

    def decorated(func):
        def inner(request, *args, **kwargs):
            response = verify_antispam_value(request, field_name)
            if response:
                return response
            else:
                return func(request, *args, **kwargs)
        return wraps(func, assigned=available_attrs(func))(inner)

    if func is None:
        def decorator(func):
            return decorated(func)
        return decorator

    return decorated(func)


def antispam_exempt(view_func):
    """
        Mark view as exempt from antispam validation
    """
    # borrowing liberally from django's csrf_exempt
    def wrapped(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped.antispam_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped)


def check_spam_ip(ip):
    return cache.get('banned_ip:%s' % ip)


def set_spam_ip(ip):
    cache.set('banned_ip:%s' %
              ip, True, settings.COMMENTS_ANTISPAM_BAN_INTERVAL)
