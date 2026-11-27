"""Views for the Online Course app, including the exam submission and results."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Choice, Course, Enrollment, Submission

PASSING_PERCENTAGE = 70


def course_list(request):
    courses = Course.objects.all()
    return render(request, 'onlinecourse_app/course_list_bootstrap.html', {'courses': courses})


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'onlinecourse_app/course_details_bootstrap.html', {'course': course})


@login_required
def exam(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    return render(request, 'onlinecourse_app/exam.html', {'course': course})


@login_required
def submit(request, course_id):
    """Store the learner's choices in a Submission and send them to the results page."""
    course = get_object_or_404(Course, pk=course_id)
    enrollment, _ = Enrollment.objects.get_or_create(user=request.user, course=course)

    submission = Submission.objects.create(enrollment=enrollment)
    # Each question posts its own radio group: choice_<question_id>.
    selected_choice_ids = [
        value for key, value in request.POST.items() if key.startswith('choice')
    ]
    for choice_id in selected_choice_ids:
        choice = Choice.objects.filter(pk=choice_id, question__course=course).first()
        if choice is not None:
            submission.choices.add(choice)
    submission.save()

    return redirect(reverse(
        'onlinecourse_app:show_exam_result',
        kwargs={'course_id': course.id, 'submission_id': submission.id},
    ))


@login_required
def show_exam_result(request, course_id, submission_id):
    """Grade the submission and render the detailed exam results."""
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission, pk=submission_id, enrollment__course=course
    )
    selected_choices = submission.choices.all()

    total_score = 0
    max_score = 0
    results = []
    for question in course.question_set.all().order_by('id'):
        max_score += question.grade
        selected = selected_choices.filter(question=question).first()
        correct_choice = question.choice_set.filter(is_correct=True).first()
        is_correct = selected is not None and selected.is_correct
        if is_correct:
            total_score += question.grade
        results.append({
            'question': question,
            'selected': selected,
            'correct_choice': correct_choice,
            'is_correct': is_correct,
        })

    score_percentage = round(total_score / max_score * 100, 2) if max_score else 0
    context = {
        'course': course,
        'submission': submission,
        'results': results,
        'total_score': total_score,
        'max_score': max_score,
        'score_percentage': score_percentage,
        'passed': score_percentage >= PASSING_PERCENTAGE,
        'passing_percentage': PASSING_PERCENTAGE,
    }
    return render(request, 'onlinecourse_app/exam_result_bootstrap.html', context)
