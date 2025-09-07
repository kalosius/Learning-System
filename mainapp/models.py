# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Institution(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="institutions/logos/", null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=32, null=True, blank=True)
    address = models.TextField(blank=True)
    timezone = models.CharField(max_length=64, default="Africa/Kampala")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=32,
        choices=[
            ("owner", "Owner"),
            ("admin", "Admin"),
            ("teacher", "Teacher"),
            ("student", "Student"),
            ("parent", "Parent"),
            ("accountant", "Accountant"),
        ],
        default="student",
    )


class AcademicYear(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)  # e.g., 2025/2026
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)


    class Meta:
        unique_together = ("institution", "name")


class Term(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.CharField(max_length=64) # Term 1, Term 2, etc.
    start_date = models.DateField()
    end_date = models.DateField()


    class Meta:
        unique_together = ("academic_year", "name")

class Department(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)


    class Meta:
        unique_together = ("institution", "name")


class Program(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)


    class Meta:
        unique_together = ("institution", "code")

class Course(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    program = models.ForeignKey(Program, null=True, blank=True, on_delete=models.SET_NULL)
    credits = models.DecimalField(max_digits=4, decimal_places=1, default=3)
    is_published = models.BooleanField(default=False)


    class Meta:
        unique_together = ("institution", "code")


class CourseRun(models.Model): # aka Section/Offering in a specific term
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, default="Main")
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teaching_runs", blank=True)
    capacity = models.PositiveIntegerField(default=0) # 0 = unlimited
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


    class Meta:
        unique_together = ("course", "term", "name")


class Enrollment(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    course_run = models.ForeignKey(CourseRun, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        unique_together = ("course_run", "student")


class Module(models.Model):
    course_run = models.ForeignKey(CourseRun, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ["order", "id"]

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)


    class Meta:
        ordering = ["order", "id"]

class Content(models.Model):
    CONTENT_TYPES = [
    ("text", "Text"), ("file", "File"), ("video", "Video"), ("link", "Link"),
    ("quiz", "Quiz"), ("assignment", "Assignment")
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    type = models.CharField(max_length=16, choices=CONTENT_TYPES)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True) # for text/HTML
    file = models.FileField(upload_to="content/files/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    link_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)


    class Meta:
        ordering = ["order", "id"]

class Assignment(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE, related_name="assignment")
    instructions = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    max_points = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    allow_late = models.BooleanField(default=False)
    late_penalty_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)


class Quiz(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE, related_name="quiz")
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    attempts_allowed = models.PositiveIntegerField(default=1)
    shuffle_questions = models.BooleanField(default=True)
    shuffle_choices = models.BooleanField(default=True)
    pass_mark_percent = models.DecimalField(max_digits=5, decimal_places=2, default=50)

class Question(models.Model):
    QUIZ_TYPES = [("mcq", "Multiple Choice"), ("tf", "True/False"), ("short", "Short Answer"), ("numeric", "Numeric")]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    type = models.CharField(max_length=16, choices=QUIZ_TYPES, default="mcq")
    points = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ["order", "id"]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="submissions/", blank=True, null=True)
    text_answer = models.TextField(blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="graded_submissions")
    graded_at = models.DateTimeField(null=True, blank=True)

class QuizResponse(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)
    text_answer = models.TextField(blank=True)
    numeric_answer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ("submission", "question")



# Track whether students attended a live class or an online session.
class Attendance(models.Model):
    course_run = models.ForeignKey(CourseRun, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=16,
        choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late")],
        default="present",
    )



# Submissions already store scores, but institutions often want a summary per term or course.
class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    letter_grade = models.CharField(max_length=2, blank=True)  # e.g., A, B, C
    calculated_at = models.DateTimeField(auto_now_add=True)

# Institutions usually need a bulletin board or notifications for students/teachers.
class Announcement(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    course_run = models.ForeignKey(CourseRun, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# For student–teacher communication or peer discussions.
class Discussion(models.Model):
    course_run = models.ForeignKey(CourseRun, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# Small institutions often need fee tracking or integration with payment gateways.
class Payment(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=128, unique=True)
    status = models.CharField(
        max_length=16,
        choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    

