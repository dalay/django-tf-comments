from django import template
from comments import settings

register = template.Library()


@register.inclusion_tag('comments/comments_antispam_field.html')
def render_antispam_field(field_name=None):
    """
        Renders antispam field named field_name (defaults to COMMENTS_ANTISPAM_FIELD_NAME).
    """
    field_name = field_name or settings.COMMENTS_ANTISPAM_FIELD_NAME
    value = settings.COMMENTS_ANTISPAM_VALUE
    if callable(value):
        value = value()
    return {'fieldname': field_name, 'value': value}
