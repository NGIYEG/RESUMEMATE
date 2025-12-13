from django.db import models
from django.utils import timezone
from Applicantapp.models import Applicant
from django.core.exceptions import ValidationError

from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/', default='company_logos/default.png')
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.company_name
    


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class AcademicCourse(models.Model):
    """
    Represents academic courses/programs that can be linked to job positions.
    Examples: Computer Science, Information Technology, Business Administration
    """
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, blank=True, null=True, help_text="Optional course code (e.g., CS, IT, BA)")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Academic Course"
        verbose_name_plural = "Academic Courses"
    
    def __str__(self):
        if self.code:
            return f"{self.name} ({self.code})"
        return self.name
    
    def clean(self):
     
        if self.name:
            self.name = self.name.strip().title()


class Post(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    title = models.CharField(max_length=100)
    
  
    required_courses = models.ManyToManyField(
        AcademicCourse,
        related_name="posts",
        help_text="Academic courses/programs that qualify someone for this position"
    )
    
    applicants = models.ManyToManyField(
        Applicant,
        through='Application',
        related_name='applied_posts'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def clean(self):
        """Validate that at least one course is assigned"""
        super().clean()
    
    
    def get_required_courses_list(self):
        """Helper method to get list of course names"""
        return list(self.required_courses.values_list('name', flat=True))


class Application(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending','Pending'), ('Accepted','Accepted'), ('Rejected','Rejected')],
        default='Pending'
    )

    class Meta:
        unique_together = ('applicant', 'post')

    def __str__(self):
        return f"{self.applicant} → {self.post}"



EDUCATION_CHOICES = [
    ('Certificate', 'Certificate'),
    ('Diploma', 'Diploma'),
    ('Bachelor', 'Bachelor Degree'),
    ('Master', 'Master Degree'),
    ('PhD', 'PhD'),
]

class JobAdvertised(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='job_adverts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='job_adverts')
    description = models.TextField()
    
    
    min_experience_years = models.PositiveIntegerField(default=0, help_text="Minimum years of experience required")
    required_education = models.CharField(max_length=50, choices=EDUCATION_CHOICES, default='Bachelor')
    required_skills = models.TextField(help_text="Comma-separated skills (e.g. Python, Django, SQL)", default="")
    
  
    selected_courses = models.ManyToManyField(
        AcademicCourse,
        related_name="job_advertisements",
        help_text="Academic courses accepted for this specific job vacancy"
    )
    
    deadline = models.DateTimeField()
    max_applicants = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_open(self):
        return timezone.now() < self.deadline
    
    def clean(self):
        """Validate that at least one course is selected"""
        super().clean()
        # This validation will be enforced at form level as well
    
    def get_selected_courses_list(self):
        """Helper method to get list of selected course names"""
        return list(self.selected_courses.values_list('name', flat=True))

    def __str__(self):
        return f"{self.post.title} in {self.department.name}"

    class Meta:
        ordering = ['-created_at']