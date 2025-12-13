from . import views
from django.urls import path

urlpatterns = [
    # path('', views.index, name='index')
     path('', views.job_feed, name='job_feed'),
     path('apply/', views.apply_for_job, name='apply_job'),
     path('insights/<int:applicant_id>/', views.view_resume_insights, name='resume_insights'),
    

]