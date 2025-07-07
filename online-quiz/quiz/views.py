from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, Answer, Subject, TestResult
from django.contrib.auth import login
from .forms import SignUpForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import random
import time

@login_required
def history_view(request):
    results = request.user.test_results.order_by('-date_taken')
    return render(request, 'quiz/history.html', {'results': results})

@csrf_exempt
def end_quiz_early(request, subject_id):
    return redirect('quiz_result', subject_id=subject_id)

def home(request):
    return render(request, 'quiz/home.html')


def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'quiz/subject_list.html', {'subjects': subjects})


def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    questions = Question.objects.filter(subject=subject)
    return render(request, 'quiz/subject_detail.html', {'subject': subject, 'questions': questions})


def subject_questions(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    questions = Question.objects.filter(subject=subject)
    return render(request, 'quiz/subject_questions.html', {
        'subject': subject,
        'questions': questions
    })


def question_list(request):
    questions = Question.objects.all()
    return render(request, 'quiz/question_list.html', {'questions': questions})


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    result = None

    if request.method == 'POST':
        selected_id = request.POST.get('answer')
        if selected_id:
            selected_answer = Answer.objects.get(id=selected_id)
            result = selected_answer.is_correct

    return render(request, 'quiz/question_detail.html', {'question': question, 'result': result})


def singup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'quiz/singup.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profile_view(request):
    profile = request.user.userprofile
    test_results = TestResult.objects.filter(user=request.user).order_by('-date_taken')

    # Додаємо хвилини і секунди до кожного результату для зручності в шаблоні
    for result in test_results:
        result.minutes = result.duration // 60
        result.seconds = result.duration % 60

    # Обчислення загального часу
    total_time = sum(result.duration for result in test_results)
    total_hours = total_time // 3600
    total_minutes = (total_time % 3600) // 60

    # Середній час на тест
    tests_count = profile.tests_taken if profile.tests_taken > 0 else 1
    avg_time = total_time // tests_count
    avg_hours = avg_time // 3600
    avg_minutes = (avg_time % 3600) // 60
    avg_seconds = avg_time % 60

    # Середній бал
    average_score = profile.total_score / tests_count if profile.tests_taken > 0 else 0

    context = {
        'profile': profile,
        'test_results': test_results,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
        'average_score': round(average_score, 2),
        'avg_hours': avg_hours,
        'avg_minutes': avg_minutes,
        'avg_seconds': avg_seconds,
    }
    return render(request, 'quiz/profile.html', context)

def start_quiz(request, subject_id):
    if 'start_time' not in request.session:
        request.session['start_time'] = time.time()

    subject = get_object_or_404(Subject, id=subject_id)
    
    question_ids = list(Question.objects.filter(subject=subject).values_list('id', flat=True))

    import random
    random.shuffle(question_ids)

    request.session['score'] = 0
    request.session['question_order'] = question_ids
    request.session['all_questions_total'] = len(question_ids)
    request.session['question_index'] = 0
    request.session['skipped_questions'] = []
    request.session['initial_question_order'] = question_ids
    

    request.session["start_time"] = time.time()

    request.session.pop('result_saved', None)
    
    return redirect('quiz_question', subject_id=subject.id, question_index=0)

def quiz_question(request, subject_id, question_index):
    start_time = request.session.get('start_time')
    if start_time:
        elapsed = time.time() - start_time
        if elapsed > 300: 
            return redirect('quiz_result', subject_id=subject_id)

    question_ids = request.session.get('question_order', [])
    skipped = request.session.get('skipped_questions', [])

    if question_index >= len(question_ids):
        if skipped:
            request.session['question_order'] = skipped
            request.session['skipped_questions'] = []
            request.session['question_index'] = 0
            return redirect('quiz_question', subject_id=subject_id, question_index=0)
        else:
            return redirect('quiz_result', subject_id=subject_id)

    question = get_object_or_404(Question, id=question_ids[question_index])
    answers = question.answers.all()

    if request.method == 'POST':
        if 'score' not in request.session:
            request.session['score'] = 0

        if 'end' in request.POST:
            return redirect('quiz_result', subject_id=subject_id)

        elif 'skip' in request.POST:
            if question.id not in skipped:
                skipped.append(question.id)
                request.session['skipped_questions'] = skipped

        elif 'answer' in request.POST:
            selected_answer_id = request.POST.get('answer')
            if selected_answer_id:
                try:
                    selected_answer = get_object_or_404(Answer, id=int(selected_answer_id))
                    if selected_answer.is_correct:
                        request.session['score'] += 1
                except ValueError:
                    pass

        return redirect('quiz_question', subject_id=subject_id, question_index=question_index + 1)

    return render(request, 'quiz/quiz_question.html', {
        'question': question,
        'answers': answers,
        'question_index': question_index + 1,
        'total': len(question_ids),
        'subject_id': subject_id,
    }) 

def quiz_result(request, subject_id):
    question_order = request.session.get('question_order', [])
    skipped_question_ids = request.session.get('skipped_questions', [])
    subject = Subject.objects.get(id=subject_id)
    all_question_ids = list(set(question_order + skipped_question_ids))
    total = len(all_question_ids)

    skipped_questions = Question.objects.filter(id__in=skipped_question_ids)

    start_time = request.session.get('start_time')
    
    # ✅ Додаємо фіксацію end_time один раз
    if 'end_time' not in request.session:
        request.session['end_time'] = time.time()

    end_time = request.session.get('end_time')
    duration = int(end_time - start_time) if start_time and end_time else 0

    score = request.session.get('score', 0)

    context = {
        'total': total,
        'skipped': len(skipped_question_ids),
        'skipped_questions': skipped_questions,
        'subject_id': subject_id,
        'duration': duration,
        'quiz': subject,
        'score': score,
        'show_result': True,
    }

    if request.user.is_authenticated and not request.session.get('result_saved'):
        profile = request.user.userprofile
        profile.tests_taken += 1
        profile.total_score += score
        profile.total_time_spent += duration
        profile.save()

        TestResult.objects.create(
            user=request.user,
            subject=subject,
            score=score,
            total_questions=total,
            skipped_questions=len(skipped_question_ids),
            duration=duration,
        )

        request.session['result_saved'] = True

    return render(request, 'quiz/quiz_result.html', context)

def correct_answers(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    questions = Question.objects.filter(subject=subject).prefetch_related('answers')

    questions_with_answers = []
    for q in questions:
        correct = q.answers.filter(is_correct=True).first()
        questions_with_answers.append({
            'text': q.text,
            'correct_answer': correct.text if correct else "Немає правильної відповіді"
        })

    context = {
        'subject': subject,
        'questions': questions_with_answers,
    }

    return render(request, 'quiz/correct_answers.html', context)


def review_answers(request, subject_id):
    question_ids = request.session.get('initial_question_order', [])
    questions = Question.objects.filter(id__in=question_ids)

    data = []
    for question in questions:
        correct = question.answers.filter(is_correct=True)
        data.append({
            'question': question,
            'correct_answers': correct
        })

    return render(request, 'quiz/review_answers.html', {
        'questions_data': data
    })

    