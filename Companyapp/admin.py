from django.contrib import admin
from .models import JobAdvertised, Post, Application, Department, AcademicCourse

# Register AcademicCourse with custom admin
@admin.register(AcademicCourse)
class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']
    ordering = ['name']

# Register Post with improved display
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'get_courses_count', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['title', 'department__name']
    filter_horizontal = ['required_courses']  # Better UI for many-to-many
    
    def get_courses_count(self, obj):
        return obj.required_courses.count()
    get_courses_count.short_description = 'Required Courses'

# Register JobAdvertised with improved display
@admin.register(JobAdvertised)
class JobAdvertisedAdmin(admin.ModelAdmin):
    list_display = ['post', 'department', 'is_open', 'deadline', 'get_courses_count', 'created_at']
    list_filter = ['department', 'created_at', 'required_education']
    search_fields = ['post__title', 'department__name', 'description']
    filter_horizontal = ['selected_courses']  # Better UI for many-to-many
    readonly_fields = ['created_at']
    
    def get_courses_count(self, obj):
        return obj.selected_courses.count()
    get_courses_count.short_description = 'Accepted Courses'

# Register remaining models
admin.site.register(Application)
admin.site.register(Department)