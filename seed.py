"""Create demo data for the Online Course app (course, lessons, exam, users)."""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlinecourse.settings')
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.core.files import File  # noqa: E402

from onlinecourse_app.models import (  # noqa: E402
    Choice, Course, Enrollment, Instructor, Learner, Lesson, Question,
)

QUESTIONS = [
    (
        'Which HTTP method should a Django form use to change data on the server?',
        [('POST', True), ('GET', False), ('HEAD', False)],
    ),
    (
        'Which file maps URL patterns to the views of a Django app?',
        [('models.py', False), ('urls.py', True), ('admin.py', False)],
    ),
    (
        'What does the {% csrf_token %} template tag protect against?',
        [('SQL injection', False), ('Cross-Site Request Forgery', True), ('Cross-Site Scripting', False)],
    ),
    (
        'Which model field creates a many-to-many relationship?',
        [('ForeignKey', False), ('ManyToManyField', True), ('OneToOneField', False)],
    ),
    (
        'What does python manage.py migrate do?',
        [('Applies database migrations', True), ('Starts the development server', False), ('Creates a new app', False)],
    ),
]


def make_course_image(path):
    """Draw a simple course cover so the ImageField has a real file."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 900, 480
    image = Image.new('RGB', (width, height), '#0d1b2a')
    draw = ImageDraw.Draw(image)
    for y in range(height):
        shade = int(20 + 60 * y / height)
        draw.line([(0, y), (width, y)], fill=(shade, shade + 25, 70 + shade))
    draw.rectangle([60, 60, width - 60, height - 60], outline='#44b78b', width=4)

    font_path = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
    try:
        title_font = ImageFont.truetype(font_path, 54)
        sub_font = ImageFont.truetype(font_path, 30)
    except OSError:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    draw.text((100, 160), 'Django Web Development', fill='white', font=title_font)
    draw.text((100, 250), 'Models, views, templates and exams', fill='#8fd6bf', font=sub_font)
    image.save(path, 'JPEG', quality=90)


def main():
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True},
    )
    if created:
        admin.set_password('Admin@12345')
        admin.save()

    learner_user, created = User.objects.get_or_create(
        username='learner', defaults={'email': 'learner@example.com'}
    )
    if created:
        learner_user.set_password('Learner@12345')
        learner_user.save()

    instructor, _ = Instructor.objects.get_or_create(
        first_name='John', last_name='Doe', user=admin
    )
    Learner.objects.get_or_create(
        user=learner_user,
        defaults={'occupation': 'Student', 'social_link': 'https://example.com/learner'},
    )

    os.makedirs('media/course_images', exist_ok=True)
    image_path = 'media/course_images/django_web_development.jpg'
    if not os.path.exists(image_path):
        make_course_image(image_path)

    course, created = Course.objects.get_or_create(
        name='Django Web Development',
        defaults={
            'description': (
                'Build a database-backed online course application with Django: models, '
                'admin, views, templates and a graded exam with automatic evaluation.'
            ),
            'pub_date': '2026-11-27',
            'total_enrollment': 2,
        },
    )
    if created:
        with open(image_path, 'rb') as handle:
            course.image.save('django_web_development.jpg', File(handle), save=True)
    course.instructors.add(instructor)

    lessons = [
        ('Introduction to Django', 'Install Django, create a project and an app, and run the development server.'),
        ('Models and databases', 'Define Course, Lesson and Enrollment models and apply migrations.'),
        ('Views and templates', 'Render course details with Django template tags and Bootstrap.'),
        ('Adding the assessment feature', 'Add Question, Choice and Submission models, then grade a mock exam.'),
    ]
    for order, (title, content) in enumerate(lessons, start=1):
        Lesson.objects.get_or_create(
            course=course, order=order, defaults={'title': title, 'content': content}
        )

    assessment_lesson = Lesson.objects.get(course=course, order=4)
    for content, choices in QUESTIONS:
        question, created = Question.objects.get_or_create(
            course=course,
            content=content,
            defaults={'grade': 20, 'lesson': assessment_lesson},
        )
        if created:
            for choice_content, is_correct in choices:
                Choice.objects.create(
                    question=question, content=choice_content, is_correct=is_correct
                )

    for user in (admin, learner_user):
        Enrollment.objects.get_or_create(user=user, course=course, defaults={'mode': 'honor'})

    print(f'Course: {course.name} ({course.id})')
    print(f'Lessons: {course.lesson_set.count()}')
    print(f'Questions: {course.question_set.count()}')
    print(f'Admin: admin / Admin@12345')


if __name__ == '__main__':
    main()
