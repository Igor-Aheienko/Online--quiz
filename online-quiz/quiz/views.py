from django.shortcuts import render, get_object_or_404
from .models import Question


def question_list(request):
    questions = Question.objects.all()
    return render(request, 'quiz/question_list.html', {'questions': questions})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'quiz/question_detail.html', {'question': question})