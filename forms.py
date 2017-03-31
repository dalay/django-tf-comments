from django.forms import ModelForm, CharField, ValidationError
from comments.models import Comment


class CommentForm(ModelForm):
    '''
    Форма для нового или редактируемого комментария.
    '''
    name = CharField(max_length=40, min_length=3, label='Ваше имя', required=True)

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
        '''
        user = kwargs.pop('user')
        # now kwargs doesn't contain 'user', so we can safely pass it to the
        # base class method
        super(CommentForm, self).__init__(*args, **kwargs)
        # Убираем поле статуса, если юзер не админ.
        if not user.is_staff:
            del self.fields["status"]
        # Убираем поле имени, если пользователь авторизован. Оно будет 
        # подставлено автоматом.
        if user is not None and not user.is_anonymous():
            del self.fields["name"]

    # def clean(self):
    #     cleaned_data = super(CommentForm, self).clean()
    #     comment = cleaned_data.get("comment")
    #     if len(comment.split()) < 3:
    #         msg = "Must put 'help' in subject when cc'ing yourself."
    #         self.add_error('comment', msg)
    #     raise ValidationError(
    #         "Did not send for 'help' in the subject despite "
    #         "CC'ing yourself."
    #     )
