from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.auth.decorators import login_required

from cnc_grader.grader_web.views import (
    CurrentProblemView, SubmitProblemView, TeamScoreView, UserSubmissionsView)

admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^submit/', login_required(SubmitProblemView.as_view()),
                     name="submitproblem"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', login_required(UserSubmissionsView.as_view()),
                    name="usersubmissionview"),
    url(r'^problem/', login_required(CurrentProblemView.as_view()),
                    name="currentproblemview"),
    url(r'^/?$', login_required(TeamScoreView.as_view()),
                 name="teamscoreview"),
)
