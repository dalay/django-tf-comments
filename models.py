from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from comments.signals import comment_added_onmoderate


class CommentCashedManager(models.Manager):
    '''
    Менеджер для получение кэшированных результатов запростов.
    '''
    @classmethod
    def cache_key(cls, *args):
        return 'comments:%s' % (':'.join(str(x) for x in args))

    def object_comments_count(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        key = self.cache_key('comments_count', ct.pk, obj.pk)
        count = cache.get(key)
        if not count:
            count = Comment.objects.filter(object_id=obj.pk,
                                           content_type=ct).count()
            if count:
                cache.set(key, count)
        return count


class Comment(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('self', related_name="childs",
                               verbose_name=_('parent comment'), blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name=_('user'), blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(_('name'), max_length=60, blank=True, null=True)
    comment = models.TextField(_('comment'), max_length=3000)
    email = models.EmailField(blank=True)
    ip_address = models.GenericIPAddressField('IP', blank=True, null=True)
    created = models.DateTimeField(_('created'),
                                   auto_now_add=True, db_index=True, editable=True)
    updated = models.DateTimeField(_('updated'),
                                   auto_now=True, editable=False)
    status = models.BooleanField(_('published'), db_index=True, default=True)
    is_new = models.BooleanField(default=True, editable=False)

    cached = CommentCashedManager()
    objects = models.Manager()

    class Meta:
        # По-умолчанию сортируем по нисходящей: сначала - последние комменты.
        # Можно изменить в темплейт-теге вызова комментов для объекта.
        ordering = ['-created']
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

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
