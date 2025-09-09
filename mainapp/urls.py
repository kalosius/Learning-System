from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # User Registration & Login
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Courses
    path('courses/', views.CourseListView.as_view(), name='courses_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='courses_detail'),
    path('courses/<int:pk>/enroll/', views.enroll_course, name='courses_enroll'),

    # Modules & Lessons
    path('modules/<int:pk>/', views.ModuleDetailView.as_view(), name='modules_detail'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='modules_lesson_detail'),

    # Assignments
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignments_detail'),
    path('assignments/<int:pk>/submit/', views.submit_assignment, name='assignments_submit'),

    # Quizzes
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quizzes_detail'),
    path('quizzes/<int:pk>/submit/', views.submit_quiz, name='quizzes_submit'),
    path('quizzes/responses/<int:pk>/', views.QuizResponseView.as_view(), name='quizzes_quiz_response'),

    # Users
    path('profile/', views.profile, name='users_profile'),
    path('users/', views.UserListView.as_view(), name='users_user_list'),

    # Announcements
    path('announcements/', views.AnnouncementListView.as_view(), name='announcements_list'),
]
