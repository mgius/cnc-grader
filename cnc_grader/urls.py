from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.auth.decorators import login_required

from cnc_grader.grader_web.views import TeamScoreView, UserSubmissionsView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cnc_grader.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    (r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', login_required(UserSubmissionsView.as_view())),
    url(r'^/?$', login_required(TeamScoreView.as_view())),
)
