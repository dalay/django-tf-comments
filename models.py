from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from comments.signals import comment_added_onmoderate


class Comment(models.Model):

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    parent = models.ForeignKey('self', related_name="childs",
                               blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField('имя', max_length=60, blank=True, null=True)
    comment = models.TextField('комментарий', max_length=3000)
    email = models.EmailField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    # Нижеследующая строка нужна для правильного экспорта из Drupal.
    # После экспорта ее нужно будет заменить на закомментированную ниже.
    # created = models.DateTimeField('дата создания', editable=True)
    created = models.DateTimeField('дата создания',
                                   auto_now_add=True, db_index=True, editable=True)

    updated = models.DateTimeField('дата последнего изменения',
                                   auto_now=True, editable=False)
    status = models.BooleanField('Опубликовано', db_index=True, default=True)

    class Meta:
        ordering = ["created"]

    @property
    def get_comment_name(self):
        '''
        Получаем значение для имени пользователя, оставившего коммент.
        Если это аноним, то используем поле 'name'.
        Если зарегиный - используем объект пользователя.
        '''
        if self.name:
            return self.name
        return self.user

    @property
    def short_comment_text(self):
        '''
        Получаем "короткий" текст из поля с комментом.
        '''
        comment = self.comment
        comment = (comment[:50] + '...') if len(comment) > 50 else comment
        return comment

    def save(self, *args, **kwargs):
        '''
        При сохранении коммента отправляем соответствующий сигнал.
        '''
        super(Comment, self).save(*args, **kwargs)
        if not self.status:
            comment_added_onmoderate.send(sender=self.__class__, comment=self)

    def __str__(self):
        return self.short_comment_text

    def get_absolute_url(self):
        return self.get_obj_absolute_url() + "#comment-%d" % self.pk

    def get_obj_absolute_url(self):
        '''
        Получаем url объекта, к которому текущий коммент принадлежит.
        '''
        return self.content_object.get_absolute_url()
