from django.urls import path
from comments import views
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


urlpatterns = [
    # Adding a new comment.
    path('new/<int:content_type_id>/<int:object_id>/',
         views.CommentCreate.as_view(), name='comment-new'),
    # Editing a comment (if there are rights for this).
    path('edit/<int:pk>/',
         login_required(views.CommentUpdate.as_view()), name='comment-edit'),
    # Delete a comment.
    path('delete/<int:pk>/',
         login_required(views.CommentDelete.as_view()), name='comment-delete'),
    # Reply to comment.
    path('reply/<int:pk>/', views.CommentReply.as_view(), name='comment-reply'),
    # A page with a list of unpublished comments.
    path('unpublished/', views.UnpublishedCommentsList.as_view(),
         name='comments-unpubleshed-list'),
    # Switching comment status (published/unpublished).
    path('toggle-status/<int:pk>/',
         staff_member_required(views.comment_status_toggle),
         name='comment-status-toggle'),
]
