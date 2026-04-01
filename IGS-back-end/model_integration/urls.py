from django.urls import path
from . import views

urlpatterns = [
    # path('predict/', views.predict, name='model_predict'),  
    path('cognitiveDiagnosis/', views.cognitiveDiagnosis, name='cognitive_diagnosis'),
    path('predictNextQuestions/', views.predict_next_questions, name='predict_next_questions'),
    path('mappingCoverage/', views.mappingCoverage, name='mapping_coverage'),
]