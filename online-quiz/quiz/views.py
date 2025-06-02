from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer, Subject
from django.contrib.auth import login
from .forms import SignUpForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import random
import time

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
            return redirect('question_list')
    else:
        form = SignUpForm()
    return render(request, 'quiz/singup.html', {'form': form})

@login_required
def profile_view(request):
    profile = request.user.userprofile
    average_score = round(profile.total_score / profile.tests_taken, 2) if profile.tests_taken > 0 else 0

    return render(request, 'quiz/profile.html', {
        'profile': profile,
        'average_score': average_score,
    })


def start_quiz(request, subject_id):
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
    request.session['start_time'] = time.time()
    request.session.pop('result_saved', None)
    

    return redirect('quiz_question', subject_id=subject.id, question_index=0)


def quiz_question(request, subject_id, question_index):
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
        if 'skip' in request.POST:
            skipped.append(question.id)
            request.session['skipped_questions'] = skipped
        else:
            selected_answer_id = int(request.POST.get('answer'))
            selected_answer = get_object_or_404(Answer, id=selected_answer_id)

            if selected_answer.is_correct:
                request.session['score'] += 1

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

    all_question_ids = list(set(question_order + skipped_question_ids))
    total = len(all_question_ids)

    skipped_questions = Question.objects.filter(id__in=skipped_question_ids)

    
    start_time = request.session.get('start_time')
    if start_time:
        duration = int(time.time() - start_time)
    else:
        duration = None

    context = {
        'total': total,
        'skipped': len(skipped_question_ids),
        'skipped_questions': skipped_questions,
        'subject_id': subject_id,
        'duration': duration,  
    }

    if request.user.is_authenticated:
        score = request.session.get('score', 0)
        context['score'] = score
        context['show_result'] = True
        context['duration'] = duration

        profile = request.user.userprofile
        profile.tests_taken += 1
        profile.total_score += context['score']
        profile.save()
    
    if request.user.is_authenticated:
        if not request.session.get('result_saved'):
            profile = request.user.userprofile
            profile.tests_taken += 1
            profile.total_score += score
            profile.save()

        request.session['result_saved'] = True

    return render(request, 'quiz/quiz_result.html', context)


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
