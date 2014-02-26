from django.contrib import admin
from cnc_grader.grader_web.models import Problem, TestCase, Submission

# Register your models here.
admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submission)
