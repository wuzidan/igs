from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict, name='model_predict'),
    path('cognitiveDiagnosis/', views.cognitiveDiagnosis, name='cognitive_diagnosis'),
]