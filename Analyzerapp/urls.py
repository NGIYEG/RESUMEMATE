from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path('job/<int:job_id>/', views.job_analytics, name='job_analytics'),
]
