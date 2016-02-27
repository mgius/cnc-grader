from django.conf.urls import patterns, include, url

from django.contrib import admin

from cnc_grader.grader_web.views import (
    CurrentProblemView, SubmitProblemView, TeamScoreView, UserSubmissionsView)

admin.autodiscover()

urlpatterns = [
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^submit/', SubmitProblemView.as_view(), name="submitproblem"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', UserSubmissionsView.as_view(), name="usersubmissionview"),
    url(r'^problem/', CurrentProblemView.as_view(), name="currentproblemview"),
    url(r'^$', TeamScoreView.as_view(), name="teamscoreview"),
]
