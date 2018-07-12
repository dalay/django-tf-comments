from django.conf import settings

COMMENTS_ON_PAGE = getattr(settings, 'COMMENTS_ON_PAGE', 10)
# COMMENTS_ORDER_BY_DESC = True

# Antispam settings
COMMENTS_ANTISPAM_FIELD_NAME = getattr(
    settings, 'COMMENTS_ANTISPAM_FIELD_NAME', 'homepage')
COMMENTS_ANTISPAM_VALUE = getattr(settings, 'COMMENTS_ANTISPAM_VALUE', '')
COMMENTS_ANTISPAM_BAN_INTERVAL = getattr(
    settings, 'COMMENTS_ANTISPAM_BAN_INTERVAL', 600)
