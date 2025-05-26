from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),  
    path('signup/', views.signup, name='signup'),  
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
]
    
