# Django Online Course — Assessment Feature

Final project for the IBM Django course: an online course application with a graded
mock exam. The app adds the `Question`, `Choice` and `Submission` models, the admin
inlines used to author an exam, the `course_details_bootstrap.html` template, and the
`submit` / `show_exam_result` views that grade a submission and show its results.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python seed.py
python manage.py runserver
```

Open http://127.0.0.1:8000/ for the course list and http://127.0.0.1:8000/admin/
for the admin site (`admin` / `Admin@12345`).

## Layout

- `onlinecourse_app/models.py` — Course, Lesson, Instructor, Learner, Enrollment, Question, Choice, Submission
- `onlinecourse_app/admin.py` — QuestionInline, ChoiceInline, QuestionAdmin, LessonAdmin
- `onlinecourse_app/views.py` — course list/details, exam, `submit`, `show_exam_result`
- `onlinecourse_app/urls.py` — routes for submit and show_exam_result
- `onlinecourse_app/templates/onlinecourse_app/course_details_bootstrap.html` — course detail template
