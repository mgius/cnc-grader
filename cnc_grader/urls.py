from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login

from cnc_grader.grader_web.views import TeamScoreView, UserSubmissionsView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cnc_grader.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^accounts/login/', login),
    url(r'^login', login),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^submissions/', login_required(UserSubmissionsView.as_view())),
    url(r'^/?$', login_required(TeamScoreView.as_view())),
)
