from django.urls import path
from . import views

app_name = 'mainapp'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # User Registration & Login
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Courses
    path('courses/', views.CourseListView.as_view(), name='courses:list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='courses:detail'),
    path('courses/<int:pk>/enroll/', views.enroll_course, name='courses:enroll'),

    # Modules & Lessons
    path('modules/<int:pk>/', views.ModuleDetailView.as_view(), name='modules:detail'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='modules:lesson_detail'),

    # Assignments
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignments:detail'),
    path('assignments/<int:pk>/submit/', views.submit_assignment, name='assignments:submit'),

    # Quizzes
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quizzes:detail'),
    path('quizzes/<int:pk>/submit/', views.submit_quiz, name='quizzes:submit'),
    path('quizzes/responses/<int:pk>/', views.QuizResponseView.as_view(), name='quizzes:quiz_response'),

    # Users
    path('profile/', views.profile, name='users:profile'),
    path('users/', views.UserListView.as_view(), name='users:user_list'),

    # Announcements
    path('announcements/', views.AnnouncementListView.as_view(), name='announcements:list'),
]
