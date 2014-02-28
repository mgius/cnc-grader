from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from cnc_grader.grader_web.models import Problem, TestCase, Team, Submission


# Register your models here.
# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class TeamInline(admin.StackedInline):
    model = Team
    can_delete = False


# Define a new User admin
class TeamAdmin(UserAdmin):
    inlines = (TeamInline, )

admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.unregister(User)
admin.site.register(User, TeamAdmin)
