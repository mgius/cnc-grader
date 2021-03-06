# pylint: disable=W0232
import logging
import os
import time

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


logger = logging.getLogger(__name__)


class Team(models.Model):
    user = models.OneToOneField(User)
    score = models.IntegerField(default=0)

    @property
    def name(self):
        return self.user.username

    def __unicode__(self):
        return unicode(self.user.__unicode__())


@receiver(post_save, sender=User)
def create_team(signal, sender, instance, created,  # pylint: disable=W0613
                **kwargs):
    if created:
        Team(user=instance).save()
        logger.debug("Created Team for user %s", instance.username)


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
                        '.'.join([str(instance.team.name), time_str]),
                        filename)


class Submission(models.Model):
    team = models.ForeignKey(Team)
    problem = models.ForeignKey(Problem)
    file = models.FileField(upload_to=upload_to)
    submission_time = models.DateTimeField(auto_now_add=True)
    graded = models.BooleanField(default=False)
    passed = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    def __unicode__(self):
        return '%s submission for problem %s %s' % (
            self.team, self.problem, self.submission_time)
