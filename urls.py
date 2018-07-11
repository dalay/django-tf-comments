from django.urls import path
from comments import views
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


app_name = 'comments'
urlpatterns = [
    # Adding a new comment.
    path('new/<int:content_type_id>/<int:object_id>/',
         views.CommentCreate.as_view(), name='new'),
    # Editing a comment (if there are rights for this).
    path('edit/<int:pk>/',
         login_required(views.CommentUpdate.as_view()), name='edit'),
    # Delete a comment.
    path('delete/<int:pk>/',
         login_required(views.CommentDelete.as_view()), name='delete'),
    # Reply to comment.
    path('reply/<int:pk>/', views.CommentReply.as_view(), name='reply'),
    # A page with a list of unpublished comments.
    path('unpublished/', views.UnpublishedCommentsList.as_view(),
         name='unpubleshed-list'),
    # Switching comment status (published/unpublished).
    path('toggle-status/<int:pk>/',
         staff_member_required(views.comment_status_toggle),
         name='status-toggle'),
]
