# teacher/api/urls.py
from django.urls import path
from .views import TeacherProfileView, TeacherAvatarUploadView, SubjectListView, TeacherDashboardView

urlpatterns = [
    path('profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('dashboard/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('profile/upload-avatar/', TeacherAvatarUploadView.as_view(), name='teacher-upload-avatar'),
    path('profile/subjects/', SubjectListView.as_view(), name='teacher-subjects'),
]