# pylint: disable=W0232
import os
import time

from django.contrib.auth.models import User
from django.db import models


class Team(models.Model):
    user = models.OneToOneField(User)
    score = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.user.__unicode__())


class Problem(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __unicode__(self):
        return self.title


class TestCase(models.Model):
    problem = models.ForeignKey(Problem)
    input = models.TextField()
    output = models.TextField()

    def __unicode__(self):
        return 'TestCase for Problem %s' % (self.problem)


def upload_to(instance, filename):
    time_str = time.strftime('%Y-%m-%H-%M-%S')
    return os.path.join('submissions',
                        '.'.join([str(instance.team.id), time_str]),
                        filename)


class Submission(models.Model):
    team = models.ForeignKey(User)
    problem = models.ForeignKey(Problem)
    file = models.FileField(upload_to=upload_to)
    submission_time = models.DateTimeField(auto_now_add=True)
    graded = models.BooleanField(default=False)
    passed = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    def __unicode__(self):
        return '%s submission for problem %s %s' % (
            self.team, self.problem, self.submission_time)
