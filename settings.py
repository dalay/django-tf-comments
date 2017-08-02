from django.conf import settings

COMMENTS_ON_PAGE = getattr(settings,'COMMENTS_ON_PAGE', 10)
COMMENTS_ORDERING = getattr(settings, 'COMMENTS_ORDERING', '-created')
