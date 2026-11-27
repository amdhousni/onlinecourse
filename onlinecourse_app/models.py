"""Models for the Online Course application, including the assessment feature."""

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Instructor(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Learner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=100)
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username


class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(User, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200, default='title')
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    MODE_CHOICES = [(AUDIT, 'Audit'), (HONOR, 'Honor')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=MODE_CHOICES, default=AUDIT)
    rating = models.FloatField(default=5.0)


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='questions'
    )
    content = models.CharField(max_length=200)
    grade = models.IntegerField(default=50)

    def __str__(self):
        return self.content


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f'Submission {self.pk} - {self.enrollment.user.username}'
