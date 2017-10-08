from django.contrib import admin

from django.contrib.auth.admin import GroupAdmin
from .models import Profile

# from .models import StudentProfile
#
# class StudentProfileAdmin(admin.ModelAdmin):
#     list_display = ["user","student_number","class_of"]
#
#     class Meta:
#         model = StudentProfile
#
# admin.site.register(StudentProfile,StudentProfileAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','get_groups','wechatNumber', 'wechatNumber_active','telephoneNumber','telephoneNumber_active']


admin.site.register(Profile, ProfileAdmin)