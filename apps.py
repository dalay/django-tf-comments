from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = 'comments'
    verbose_name = _('Comments')
