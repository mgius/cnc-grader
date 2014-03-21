from django.core.urlresolvers import reverse_lazy
from django.forms import ModelForm
from django.views import generic

from cnc_grader.grader_web.models import Problem, Submission, Team


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
        return Team.objects.order_by('-score')


class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ['problem', 'file']

    def __init__(self, *args, **kwargs):  # pylint: disable=E1002
        self.request = kwargs.pop('request', None)
        super(SubmissionForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):  # pylint: disable=E1002
        kwargs['commit'] = False
        obj = super(SubmissionForm, self).save(*args, **kwargs)
        if self.request:
            obj.team = self.request.user.team
            # obj.problem = Problem.objects.order_by('-id')[0]
        obj.save()
        return obj


class SubmitProblemView(generic.CreateView):
    template_name = 'submit_problem.html'
    form_class = SubmissionForm
    success_url = reverse_lazy("usersubmissionview")

    def get_form_kwargs(self):
        """
        This is the most convoluted way to go about this...
        """
        kwargs = super(SubmitProblemView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class CurrentProblemView(generic.DetailView):
    template_name = 'problem_detail.html'
    context_object_name = 'problem'

    def get_object(self, queryset=None):
        return Problem.objects.order_by('-id')[0]
