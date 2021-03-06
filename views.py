from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required

from .models import Comment
from .forms import CommentForm


class UnpublishedCommentsList(ListView):
    '''
    Список неопубликованных комментов.
    '''
    queryset = Comment.objects.filter(
        status=False).select_related('parent', 'user')
    context_object_name = 'comments'
    paginate_by = 20
    template_name = 'comments/unpub_comments.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        '''
        Проверка доступа - только для админов.
        '''
        return super().dispatch(request, *args, **kwargs)


class CommentCommonMixin:
    '''
    "Общий" миксин для формы коммента.
    Проверяем в нем права пользователя и определяем страницу для редиректа
    после сохранения.
    '''

    def check_permissions(self, comment):
        """
        Если текущий пользователь не суперюзер и не автор
        комментария, то кидаем ему ошибку 403.
        """
        user = self.request.user
        if not user.is_staff and comment.user is not user:
            raise PermissionDenied

    def get_success_url(self):
        """
        При успешном удалении коммента перекидываем польхователя
        на страницу комментируемой публикации.
        """
        redirect = self.request.GET.get('next')
        if redirect:
            return redirect
        return self.object.get_obj_absolute_url() + '#comments'


class CommentAddUpdateMixin(CommentCommonMixin):
    '''
    Миксин для форм доваления и изменения комментария.
    '''
    model = Comment
    template_name = "comments/comment_add_edit.html"
    form_class = CommentForm

    def get_form_kwargs(self):
        """
        Передаем для формы добавдения/правки комментария
        обьект текущего пользователя.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user})
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        if request.is_ajax():
            if hasattr(self, 'is_update_view'):
                self.object = self.get_object()

            form = self.get_form()
            context = {}
            context['user'] = request.user
            context['form'] = form
            context['csrf_token'] = get_token(self.request)
            if hasattr(self, 'parent'):
                context['parent'] = self.parent
            data = {'form': render_to_string("comments/_form.html", context)}
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        '''
        Обработка аякс-запроса, когда поля формы проверены и валидны.
        '''
        response = super().form_valid(form)
        msg = ''
        # Анониму шлем мессадж о том что его коммент будет опубликован
        # только после проверки модером.
        if self.request.user.is_anonymous:
            msg = _('Comment was sent for moderation.')
        if self.request.is_ajax():
            data = {}
            if hasattr(self, 'is_update_view'):
                data['is_update_view'] = True
                data['comment_id'] = self.object.pk
            data['comment'] = render_to_string("comments/_comment.html", {
                'comment': self.object})
            if msg:
                # Если это аякс, то мессадж шлем, как дополнительное поле
                # с определенным текстом.
                data['flash_message'] = msg
            return JsonResponse(data)
        if msg:
            messages.add_message(self.request, messages.INFO, msg)
        return response

    def form_invalid(self, form):
        '''
        Обработка аякс-запроса, когда поля формы не прошли валидацию.
        '''
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return response


@method_decorator(login_required, name='dispatch')
class CommentCreate(CommentAddUpdateMixin, CreateView):
    '''
    Создание нового коммента.
    '''
    def dispatch(self, *args, **kwargs):
        """
        Присваиваем и, заодно, проверяем на существование
         тип и обьект публикации, к которой хотят запостить
          коммент.
        В зависимости от формы(ответ или новый коммент), берем
        значения из разных источников.
        """
        if hasattr(self, 'is_reply_view'):
            self.parent = get_object_or_404(Comment, pk=kwargs['pk'])
            self.obj_content_type = self.parent.content_type
            self.obj = self.parent.content_object
        else:
            self.parent = False
            self.obj_content_type = get_object_or_404(
                ContentType, pk=self.kwargs['content_type_id'])
            self.obj = get_object_or_404(self.obj_content_type.model_class(),
                                         pk=self.kwargs['object_id'])
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        '''
        После прохождения валидации определяем значение
        для поля с IP комментарора, его имени, статуса коммента, данных
        комментируемого объекта, и "родительского" коммента(если текущий коммент
        - ответ на уже имеющийся).
        '''
        user = self.request.user
        if user is not None and not user.is_anonymous:
            form.instance.user = user
            form.instance.email = user.email
        elif form.instance.name:
            self.request.session['name'] = form.instance.name
        form.instance.ip_address = get_ip_address(self.request)
        form.instance.content_type = self.obj_content_type
        if self.parent:
            form.instance.parent = self.parent
            form.instance.object_id = self.parent.object_id
        else:
            form.instance.object_id = self.kwargs['object_id']
        if user.is_anonymous:
            form.instance.status = False
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        '''
        Добавляем комментируемый объект в контекст коммента.
        '''
        context = super().get_context_data(**kwargs)
        context['object'] = self.obj
        if self.parent:
            context['parent'] = self.parent
        return context

    def get_initial(self):
        '''
        Проверияем сессию пол-ля на предмет наличия "имени".
        Если находим - подставляем в поле "name" коммента.
        '''
        name = self.request.session.get('name')
        return {
            'name': name,
        }


class CommentReply(CommentCreate):
    '''
    Ответ на коммент. Просто добавляем свойство-флаг с соответствующим значением.
    '''
    is_reply_view = True


class CommentUpdate(CommentAddUpdateMixin, UpdateView):
    '''
    Обновление комментария.
    '''
    is_update_view = True

    def form_valid(self, form):
        # redirect = self.request.GET.get('next')
        # if redirect:
        #     self.success_url = redirect
        return super().form_valid(form)

    def get_object(self, *args, **kwargs):
        '''
        Проверяем права на редактирование коммента.
        '''
        comment = super().get_object(*args, **kwargs)
        self.check_permissions(comment)
        return comment


class CommentDelete(CommentCommonMixin, DeleteView):
    '''
    Удаление комментария.
    '''

    model = Comment

    def get_object(self, *args, **kwargs):
        '''
        Проверка прав пользованетя на удаление.
        '''
        comment = super().get_object(*args, **kwargs)
        self.check_permissions(comment)
        return comment


def get_ip_address(request):
    """
    use requestobject to fetch client machine's IP Address
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        # Real IP address of client Machine
        ip = request.META.get('REMOTE_ADDR')
    return ip


@staff_member_required
def comment_status_toggle(request, pk):
    '''
    Переключение статуса комментария (опубликован/неопубликова).
    '''
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        raise Http404

    comment.status = not bool(comment.status)
    comment.save(update_fields=['status'])
    msg = _('Comment "%(comment)s" has been %(status)s') % {
        'comment': comment.short_comment_text,
        'status': 'disabled' if not comment.status else 'posted'
    }
    messages.add_message(request, messages.INFO, msg)

    next = request.GET.get('next', False)
    if next:
        return redirect(next)
    return redirect('comments:unpublished-list')
