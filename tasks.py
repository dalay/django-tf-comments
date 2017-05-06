from django_rq import job
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings
from django.dispatch import receiver
from .models import Comment
from .signals import comment_added_onmoderate


@job
def notify_comment_onmoderate(comment_pk):
    comment = Comment.objects.get(pk=comment_pk)
    subject = 'Новый комментарий на сайте'
    template = get_template('comments/notify_comment_onmoderate.html')
    context = { 
        'comment': comment,
        'base_url': getattr(settings, 'BASE_URL', '')
    }   
    content = template.render(context)
    email = EmailMessage(
        subject,
        content,
        settings.SERVER_EMAIL,
        [a[1] for a in settings.ADMINS],
    )   
    email.content_subtype = "html"
    email.send()

@receiver(comment_added_onmoderate)
def set_queue(sender, comment, **kwargs):
    notify_comment_onmoderate.delay(comment.pk)
