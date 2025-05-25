from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer, Subject
from django.contrib.auth import login
from .forms import SignUpForm


def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'quiz/subject_list.html', {'subjects': subjects})

def question_list(request):
    questions = Question.objects.all()
    return render(request, 'quiz/question_list.html', {'questions': questions})

def home(request):
    return render(request, 'quiz/home.html')


def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    questions = Question.objects.filter(subject=subject)
    return render(request, 'quiz/subject_detail.html', {'subject': subject, 'questions': questions})


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)

    result = None

    if request.method == 'POST':
        selected_id = request.POST.get('answer')
        if selected_id:
            selected_answer = Answer.objects.get(id=selected_id)
            result = selected_answer.is_correct

    return render(request, 'quiz/question_detail.html', {'question': question, 'result': result})

   

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('question_list')
    else:
        form = SignUpForm()
    return render(request, 'quiz/signup.html', {'form': form})

 
    