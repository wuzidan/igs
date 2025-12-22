# urls.py（应用内）
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExerciseViewSet, debug_view, question, question_list

app_name = 'question'

router = DefaultRouter()
router.register(r'', ExerciseViewSet, basename='exercise')

urlpatterns = [
    path('question/', question_list, name='question_list'),
    path('', include(router.urls)),
    path('page/', question.as_view(), name='question_page'),
    path('debug/', debug_view, name='debug'),
]