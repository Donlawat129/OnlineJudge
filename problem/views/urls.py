from django.urls import path
from .views import ProblemTagAPI

urlpatterns = [
    path('api/problem/tags/', ProblemTagAPI.as_view(), name="problem_tag_list_api"),
]
