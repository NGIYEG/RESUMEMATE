from django import forms
from .models import Post, Department, JobAdvertised

from django import forms
from .models import JobAdvertised

class JobAdvertisedForm(forms.ModelForm):
    class Meta:
        model = JobAdvertised
        # We added 'description', 'min_experience_years', 'required_education', 'required_skills'
        fields = [
            'department', 
            'post', 
            'description',
            'min_experience_years', 
            'required_education', 
            'required_skills',
            'deadline', 
            'max_applicants'
        ]

        widgets = {
            'department': forms.Select(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500'
            }),

            'post': forms.Select(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500'
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

            'deadline': forms.DateInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500'
            }),

            'max_applicants': forms.NumberInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500'
            }),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['department', 'title']
        widgets = {
            'department': forms.Select(attrs={
                'class': 'w-full border-[#cb8700] rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full border-[#cb8700] rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition'
            }),
        }
        
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg shadow-sm px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition'
            })
        }