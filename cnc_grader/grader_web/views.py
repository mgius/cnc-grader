from django.shortcuts import render
from django.views import generic

from cnc_grader.grader_web.models import Submission, Team

# Create your views here.
class UserSubmissionsView(generic.ListView):
    template_name = 'submissions.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        """Return the last five published polls."""
        return Submission.objects.filter(team=self.request.user.id
            ).order_by('-submission_time')[:5]

class TeamScoreView(generic.ListView):
    template_name = 'teamscore.html'
    context_object_name = 'teams'

    def get_queryset(self):
        """Return teams ordered by score."""
        return Team.objects.order_by('score')
