from django.conf.urls import url
from comments import views
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


urlpatterns = [
    url(r'^new/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        views.CommentCreate.as_view(), name='comment-new'),
    url(r'^edit/(?P<pk>\d+)/$',
        login_required(views.CommentUpdate.as_view()),
        name='comment-edit'),
    url(r'^delete/(?P<pk>\d+)/$',
        login_required(views.CommentDelete.as_view()), name='comment-delete'),
    url(r'^reply/(?P<pk>[\d-]+)/$', views.CommentReply.as_view(),
        name='comment-reply'),
    url(r'^unpublished/$', views.UnpublishedCommentsList.as_view(),
        name='comments-unpubleshed-list'),
    url(r'^toggle-status/(?P<pk>\d+)/$',
        staff_member_required(views.comment_status_toggle),
        name='comment-status-toggle'),

    # url(r'^(?P<pk>[\d-]+)/$', login_required(views.AdvertEdit.as_view()), name='comment-detail',
    # url(r'^(?P<pk>[\d-]+)/edit', login_required(views.AdvertEdit.as_view()), name='comment-edit'),
    # url(r'^(?P<pk>[\d-]+)/delete', login_required(views.AdvertEdit.as_view()), name='comment-delete'),
]
