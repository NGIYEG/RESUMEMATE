from django import forms
from Applicantapp.models import Applicant
from Companyapp.models import JobAdvertised


from django import forms
from django.contrib.auth.models import User
from .models import Applicant
from Companyapp.models import JobAdvertised


class ApplicantApplyForm(forms.ModelForm):
    job = forms.ModelChoiceField(
        queryset=JobAdvertised.objects.all(),
        widget=forms.Select(attrs={
            "class": "w-full border-gray-300 rounded-lg px-3 py-2"
        }),
        label="Select Job"
    )

    class Meta:
        model = Applicant
        fields = [
            'first_name', 'last_name', 'email',
            'linkedIn_profile', 'portfolio_link',
            'resume', 'other_documents'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'last_name': forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'email': forms.EmailInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'linkedIn_profile': forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'portfolio_link': forms.URLInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'resume': forms.FileInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'other_documents': forms.FileInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
        }



class UserRegisterForm(forms.ModelForm):
    """Handles the Account Creation (Username/Password)"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "w-full border-gray-300 rounded-lg px-3 py-2",
        "placeholder": "Password"
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "w-full border-gray-300 rounded-lg px-3 py-2",
        "placeholder": "Confirm Password"
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

        help_texts = {
            'username': None,  
        }

        widgets = {
            'username': forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'email': forms.EmailInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'first_name': forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
            'last_name': forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

# Applicantapp/forms.py

# Applicantapp/forms.py

class ApplicantProfileForm(forms.ModelForm):
    """Handles Profile Updates"""
    # These fields are mainly for the "Edit Profile" page
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-cyan-600 focus:border-cyan-600"
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-cyan-600 focus:border-cyan-600"
    }))

    class Meta:
        model = Applicant
        fields = ['profile_picture', 'bio', 'phone', 'location', 'linkedIn_profile', 'portfolio_link', 'resume']
        widgets = {
            'profile_picture': forms.FileInput(attrs={"class": "w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"}),
            'bio': forms.Textarea(attrs={"rows": 4, "class": "w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-cyan-600 focus:border-cyan-600", "placeholder": "Tell recruiters about yourself..."}),
            'phone': forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-cyan-600 focus:border-cyan-600"}),
            'location': forms.TextInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-cyan-600 focus:border-cyan-600"}),
            'linkedIn_profile': forms.URLInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-cyan-600 focus:border-cyan-600"}),
            'portfolio_link': forms.URLInput(attrs={"class": "w-full border-gray-300 rounded-lg px-3 py-2 focus:ring-cyan-600 focus:border-cyan-600"}),
            'resume': forms.FileInput(attrs={"class": "w-full text-sm text-slate-500..."}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # ✅ FIX: Check if the profile has a user before trying to update user details
        if getattr(profile, 'user', None):
            user = profile.user
            # Only update names if they were actually provided in this form
            if self.cleaned_data.get('first_name'):
                user.first_name = self.cleaned_data['first_name']
            if self.cleaned_data.get('last_name'):
                user.last_name = self.cleaned_data['last_name']
            
            if commit:
                user.save()
        
        if commit:
            profile.save()
        return profile