from django.dispatch import Signal
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
from django.conf import settings


comment_added_onmoderate = Signal(providing_args=["comment"])
comment_updated = Signal(providing_args=["comment"])

@receiver(comment_added_onmoderate)
def notify_comment_onmoderate(sender, comment, **kwargs):
    '''
    Ловим сигнал о том, что новый коммент пришел на модерацию,
    и отправляем письмо админу с уведомлением об этом событии.
    '''
    subject = 'Новый комментарий на сайте'
    template = get_template('comments/notify_comment_onmoderate.txt')
    context = Context({
        'comment': comment
    })
    content = template.render(context)
    email = EmailMessage(
        subject,
        content,
        settings.SERVER_EMAIL,
        [a[1] for a in settings.ADMINS],
    )
    email.send()
