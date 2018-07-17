from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, CharField
from comments.models import Comment
# from captcha.fields import ReCaptchaField


def check_recaptcha():
    try:
        # check installed
        # https://github.com/praekelt/django-recaptcha
        from captcha.fields import ReCaptchaField
    except ModuleNotFoundError:
        pass
    else:
        return ReCaptchaField


class CommentForm(ModelForm):
    '''
    Форма для нового или редактируемого комментария.
    '''
    name = CharField(max_length=40, min_length=3,
                     label=_('Your name'), required=True)

    class Meta:
        model = Comment
        fields = [
            "name", "comment", 'status',
        ]

    def __init__(self, *args, **kwargs):
        '''
        1. Убираем из формы коммента поле установки статуса, если
        пользователь не принадлежит к админам.
        2. Убираем поле 'name' из формы, если пользователь авторизирован.
        3. If the Recaptcha module is installed - show it to an anonymous user.
        (praekelt/django-recaptcha https://github.com/praekelt/django-recaptcha)
        '''

        user = kwargs.pop('user')
        # now kwargs doesn't contain 'user', so we can safely pass it to the
        # base class method
        super(CommentForm, self).__init__(*args, **kwargs)

        # check https://github.com/praekelt/django-recaptcha
        recaptcha_field = check_recaptcha()

        # Убираем поле статуса, если юзер не админ.
        if not user.is_staff:
            del self.fields["status"]
        # Убираем поле имени, если пользователь авторизован. Оно будет
        # подставлено автоматом.
        if user is not None and not user.is_anonymous:
            del self.fields["name"]
        elif recaptcha_field:
            self.fields["captcha"] = recaptcha_field(label='')
