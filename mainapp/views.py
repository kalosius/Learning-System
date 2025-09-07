from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.urls import reverse
from .models import (
    Course, CourseRun, Module, Lesson, Assignment, Submission, Quiz, Question,
    Choice, QuizResponse, Enrollment, User, Announcement
)
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# -----------------------
# Dashboard
# -----------------------
@login_required
def dashboard(request):
    enrolled_courses_count = Enrollment.objects.filter(student=request.user, is_active=True).count()
    pending_assignments_count = Submission.objects.filter(student=request.user, score__isnull=True).count()
    pending_quizzes_count = Quiz.objects.exclude(submission__student=request.user).count()
    return render(request, 'dashboard.html', {
        'enrolled_courses_count': enrolled_courses_count,
        'pending_assignments_count': pending_assignments_count,
        'pending_quizzes_count': pending_quizzes_count,
    })

# -----------------------
# Courses
# -----------------------
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(is_published=True)

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_modules'] = Module.objects.filter(course_run__course=self.object)
        return context

@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    run, _ = CourseRun.objects.get_or_create(course=course, term=course.program.institution.academicyear_set.first())
    Enrollment.objects.get_or_create(course_run=run, student=request.user)
    return redirect('courses:detail', pk=course.pk)




# -----------------------# Modules and Lessons
# -----------------------
# -----------------------
# Modules
# -----------------------
class ModuleDetailView(DetailView):
    model = Module
    template_name = 'modules/module_detail.html'
    context_object_name = 'module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lessons'] = Lesson.objects.filter(module=self.object)
        return context

class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'modules/lesson_detail.html'
    context_object_name = 'lesson'



# -----------------------# Assignments
# -----------------------
# -----------------------
# Assignments
# -----------------------
class AssignmentDetailView(DetailView):
    model = Assignment
    template_name = 'assignments/assignment_detail.html'
    context_object_name = 'assignment'

@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        content = request.POST.get("submission")
        Submission.objects.create(
            assignment=assignment,
            student=request.user,
            text_answer=content,
            submitted_at=timezone.now()
        )
        return redirect('assignments:detail', pk=assignment.pk)
    return redirect('assignments:detail', pk=assignment.pk)


# -----------------------# Quizzes
# -----------------------

# -----------------------
# Quizzes
# -----------------------
class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'quizzes/quiz_detail.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        return context

@login_required
def submit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == "POST":
        submission = Submission.objects.create(
            quiz=quiz,
            student=request.user,
            submitted_at=timezone.now()
        )
        for question in quiz.questions.all():
            choice_id = request.POST.get(f"question_{question.id}")
            selected_choice = Choice.objects.filter(id=choice_id).first() if choice_id else None
            QuizResponse.objects.create(
                submission=submission,
                question=question,
                selected_choice=selected_choice
            )
        return redirect('quizzes:quiz_response', pk=submission.pk)
    return redirect('quizzes:detail', pk=quiz.pk)

class QuizResponseView(DetailView):
    model = Submission
    template_name = 'quizzes/quiz_response.html'
    context_object_name = 'submission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = self.object.responses.all()
        context['score'] = sum(r.question.points for r in self.object.responses.all() if r.selected_choice and r.selected_choice.is_correct)
        context['total'] = sum(r.question.points for r in self.object.responses.all())
        return context


# users views
# -----------------------
# Users
# -----------------------
@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'



# -----------------------# Announcements
# -----------------------

# -----------------------
# Announcements
# -----------------------
class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcements/announcement_list.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        return Announcement.objects.filter(institution=self.request.user.institution)








# -----------------------
# User Registration
# -----------------------
def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("users:register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("users:register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
        )
        user.first_name = full_name.split(" ")[0]
        user.last_name = " ".join(full_name.split(" ")[1:])
        user.phone = phone
        user.save()

        messages.success(request, "Account created successfully. You can now login.")
        return redirect("users:login")

    return render(request, "users/register.html")


# -----------------------
# User Login
# -----------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("core:dashboard")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("users:login")
    return render(request, "users/login.html")


# -----------------------
# User Logout
# -----------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect("users:login")

