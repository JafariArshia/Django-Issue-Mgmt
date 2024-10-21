from django.urls import path
from . import views
from .views import IssueDetailView, SuccessView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='task_list'),
    path('issue/<int:pk>/', IssueDetailView.as_view(), name = 'task_detail'),
    path('issue/search/', views.searchContent, name = 'search'),
    path('issue/create/', views.create_issue, name = 'create_issue'),
    path('issue/filter/', views.filterContent, name = 'filter'),
    path('issue/update/<int:task_id>/', views.update_issue, name = 'update_issue'),
    path('success/', SuccessView.as_view(), name='success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    