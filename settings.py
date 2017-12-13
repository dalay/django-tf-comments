from django.conf import settings

COMMENTS_ON_PAGE = getattr(settings,'COMMENTS_ON_PAGE', 10)
# COMMENTS_ORDER_BY_DESC = True
