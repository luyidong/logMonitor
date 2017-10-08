from django.contrib import admin

from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User, Group

from .models import DataPoint,Alert

class DataPointAdmin(admin.ModelAdmin):
    list_display = ["node_name","data_type","datetime","data_value"]
    list_editable = ["data_type","data_value"]
    class Meta:
        model = DataPoint

class UserSetInline(admin.TabularInline):
    model = User.groups.through
    raw_id_fields = ('user',)  # optional, if you have too many users

class MyGroupAdmin(GroupAdmin):
    inlines = [UserSetInline]


# class AlertAdmin(admin.ModelAdmin):
#     list_display = ["data_type","min_value","max_value","node_name","get_users","get_groups","is_active"]
#     list_editable = ["data_type","is_active"]
#     class Meta:
#         model = DataPoint

# unregister and register again
admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)

admin.site.register(DataPoint,DataPointAdmin)
# admin.site.register(Alert,AlertAdmin)


