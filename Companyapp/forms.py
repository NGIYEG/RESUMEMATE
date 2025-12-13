from django import forms
from .models import Post, Department, JobAdvertised, AcademicCourse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class AcademicCourseForm(forms.ModelForm):
    """Form for creating new academic courses"""
    class Meta:
        model = AcademicCourse
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition',
                'placeholder': 'e.g., Computer Science, Information Technology'
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition',
                'placeholder': 'e.g., CS, IT, BA (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border-gray-300 rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition',
                'rows': 2,
                'placeholder': 'Optional description of the course'
            }),
        }


class PostForm(forms.ModelForm):
    """Form for creating job posts with required academic courses"""
    
    # Add a multiple choice field for courses
    required_courses = forms.ModelMultipleChoiceField(
        queryset=AcademicCourse.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'mr-2'
        }),
        required=True,
        help_text="Select at least one academic course required for this position"
    )
    
    class Meta:
        model = Post
        fields = ['department', 'title', 'required_courses']
        widgets = {
            'department': forms.Select(attrs={
                'class': 'w-full border-gray-300 rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition',
                'placeholder': 'e.g., Software Engineer, Data Analyst'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing post, pre-select the courses
        if self.instance.pk:
            self.fields['required_courses'].initial = self.instance.required_courses.all()
    
    def clean_required_courses(self):
        """Validate that at least one course is selected"""
        courses = self.cleaned_data.get('required_courses')
        if not courses or courses.count() == 0:
            raise ValidationError("You must select at least one academic course for this position.")
        return courses
    
    def clean_title(self):
        """Normalize and validate title"""
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip().title()
            
            # Check for duplicate within same department
            department = self.cleaned_data.get('department')
            if department:
                existing = Post.objects.filter(
                    department=department, 
                    title__iexact=title
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if existing.exists():
                    raise ValidationError(f"A post with title '{title}' already exists in {department.name}.")
        
        return title


class JobAdvertisedForm(forms.ModelForm):
    """Form for creating job advertisements with course selection"""
    
    # This will be dynamically populated based on selected post
    selected_courses = forms.ModelMultipleChoiceField(
        queryset=AcademicCourse.objects.none(),  # Empty initially
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'mr-2'
        }),
        required=True,
        help_text="Select which courses are accepted for this specific vacancy"
    )
    
    class Meta:
        model = JobAdvertised
        fields = [
            'department', 
            'post', 
            'description',
            'min_experience_years', 
            'required_education', 
            'required_skills',
            'selected_courses',
            'deadline', 
            'max_applicants'
        ]

        widgets = {
            'department': forms.Select(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500',
                'id': 'id_department'
            }),

            'post': forms.Select(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500',
                'id': 'id_post'
            }),

            'description': forms.Textarea(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500',
                'rows': 4,
                'placeholder': 'Describe the role responsibilities...'
            }),

            'min_experience_years': forms.NumberInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500',
                'min': 0
            }),

            'required_education': forms.Select(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500'
            }),

            'required_skills': forms.Textarea(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500',
                'rows': 2,
                'placeholder': 'e.g. Python, SQL, Django, Leadership'
            }),

            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500'
            }),

            'max_applicants': forms.NumberInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If post is already selected, populate courses
        if 'post' in self.data:
            try:
                post_id = int(self.data.get('post'))
                post = Post.objects.get(id=post_id)
                self.fields['selected_courses'].queryset = post.required_courses.all()
            except (ValueError, TypeError, Post.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.post:
            # Editing existing job - show post's courses
            self.fields['selected_courses'].queryset = self.instance.post.required_courses.all()
            self.fields['selected_courses'].initial = self.instance.selected_courses.all()
    
    def clean_selected_courses(self):
        """Validate that at least one course is selected"""
        courses = self.cleaned_data.get('selected_courses')
        post = self.cleaned_data.get('post')
        
        if not courses or courses.count() == 0:
            raise ValidationError("You must select at least one academic course for this vacancy.")
        
        # Validate that selected courses are from the post's required courses
        if post:
            valid_courses = post.required_courses.all()
            for course in courses:
                if course not in valid_courses:
                    raise ValidationError(f"Course '{course.name}' is not valid for the selected position.")
        
        return courses
    
    def clean(self):
        """Additional cross-field validation"""
        cleaned_data = super().clean()
        post = cleaned_data.get('post')
        
        # Ensure post has required courses defined
        if post and post.required_courses.count() == 0:
            raise ValidationError({
                'post': 'The selected position has no academic courses defined. Please update the position first.'
            })
        
        return cleaned_data


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition',
                'placeholder': 'e.g., Engineering, Marketing, Human Resources'
            })
        }
    
    def clean_name(self):
        """Normalize department name"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip().title()
        return 
    




from django.contrib.auth.models import User
from .models import Company

class CompanyRegisterForm(forms.ModelForm):
    # User Account Fields
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2", "placeholder": "Username"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2", "placeholder": "Company Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2", "placeholder": "Password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2", "placeholder": "Confirm Password"}))

    # Company Profile Fields
    company_name = forms.CharField(widget=forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2", "placeholder": "Company Name (e.g. TechCorp)"}))
    location = forms.CharField(widget=forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2", "placeholder": "Headquarters Location"}))
    logo = forms.ImageField(required=False, widget=forms.FileInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}))

    class Meta:
        model = Company
        fields = ['company_name', 'location', 'website', 'description', 'logo']
        widgets = {
            'website': forms.URLInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2", "placeholder": "https://..."}),
            'description': forms.Textarea(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2", "rows": 3, "placeholder": "What does your company do?"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data