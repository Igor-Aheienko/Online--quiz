from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from .views import history_view

urlpatterns = [
    path('', views.home, name='home'),  
    path('singup/', views.singup, name='singup'),  
    path('questions/', views.question_list, name='question_list'), 
    path('questions/<int:pk>/', views.question_detail, name='question_detail'), 
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:subject_id>/', views.subject_questions, name='subject_questions'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('quiz/', views.question_list, name='question_list'),
    path('quiz/<int:subject_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:subject_id>/question/<int:question_index>/', views.quiz_question, name='quiz_question'),
    path('quiz/<int:subject_id>/result/', views.quiz_result, name='quiz_result'),
    path('quiz/<int:subject_id>/end/', views.end_quiz_early, name='end_quiz_early'),
    path('review/<int:subject_id>/', views.review_answers, name='review_answers'),
    path('profile/', views.profile_view, name='profile'),
    path('quiz/<int:subject_id>/answers/', views.correct_answers, name='quiz_correct_answers'),
    path('quiz/<int:subject_id>/', views.quiz_question, name='quiz'),
    path('profile/history/', history_view, name='profile_history'),
    
]