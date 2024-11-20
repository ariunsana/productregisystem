from django.contrib import admin
from .models import Turul, Baraa, Branch, BranchBaraa, UserRole, Users, Worker, Sales

class TurulAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('turul_name',)}

class BaraaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('baraa_name',)}

class TurulAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('turul_name',)}

class BranchAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('branch_name',)}

class UserRoleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('role_name',)}

class UsersAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('username',)}

class WorkerAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('firstname',)}


admin.site.register(Turul, TurulAdmin)
admin.site.register(Baraa, BaraaAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(BranchBaraa)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Sales)
