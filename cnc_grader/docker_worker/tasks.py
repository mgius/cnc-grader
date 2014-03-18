#! /usr/bin/env python

from collections import defaultdict
import logging
import os
import shutil
import tempfile

from celery import shared_task
import docker
from django.db.models.signals import post_save
from django.dispatch import receiver

from cnc_grader.grader_web import models


logger = logging.getLogger()


@receiver(post_save, sender=models.Submission)
def submit_execute(signal, sender, instance, created, **kwargs):
    if created:
        logging.info("Submitting test run for instance id %d", instance.id)
        execute_submission.delay(instance.id)


@shared_task()
def execute_submission(submission_id):
    submission = models.Submission.objects.get(id=submission_id)
    inputs_dir = tempfile.mkdtemp()
    outputs_dir = tempfile.mkdtemp()
    submission_dir = tempfile.mkdtemp()
    c = docker.Client()
    result = 1
    logger.info("Grading submission %d for team %s",
                submission_id, submission.team.user.username)
    try:
        for testcase in submission.problem.testcase_set.all():
            infile = os.path.join(inputs_dir, '%d' % testcase.id)
            outfile = os.path.join(outputs_dir, '%d' % testcase.id)
            with open(infile, 'w') as f:
                f.write(testcase.input)

            with open(outfile, 'w') as f:
                f.write(testcase.output)

        submission_file = os.path.join(submission_dir,
                                       os.path.basename(submission.file.name))
        with open(submission_file, 'w') as f:
            f.write(submission.file.read())

        container_id = c.create_container(
            'crashandcompile',
            command=('/test_executor.py'
                     ' --inputsdir /inputs'
                     ' --outputsdir /outputs'
                     ' --submission ' +
                     os.path.join('/submission',
                                  os.path.basename(submission.file.name))),
            volumes=['/inputs/', '/outputs', '/submission'])
        logger.debug("Created container %s to execute submission %d",
                     container_id, submission_id)
        c.start(container_id,
                binds={inputs_dir: '/inputs',
                       outputs_dir: '/outputs',
                       submission_dir: '/submission'})
        # TODO: needs timeout
        result = c.wait(container_id)

    finally:
        shutil.rmtree(inputs_dir)
        shutil.rmtree(outputs_dir)
        shutil.rmtree(submission_dir)
        submission.graded = True
        submission.passed = (result == 0)
        submission.save()

        if submission.passed:
            # this is rather naive and easily abused...
            calculate_team_scores.delay()


@shared_task()
def calculate_team_scores():
    max_winners = 3
    submissions = models.Submission.objects.order_by('submission_time').all()
    teams = models.Team.objects.all()

    correct_for_problem = defaultdict(int)
    score_for_team = defaultdict(int)
    # problem -> team -> bool
    points_awarded_for_problem = defaultdict(lambda: defaultdict(bool))

    for submission in submissions:
        if not submission.passed:
            continue

        if points_awarded_for_problem[submission.problem][submission.team]:
            continue

        if correct_for_problem[submission.problem] >= max_winners:
            continue

        score_for_team[submission.team] += (
            max_winners - correct_for_problem[submission.problem])
        correct_for_problem[submission.problem] += 1
        points_awarded_for_problem[submission.problem][submission.team] = True

    for team in teams:
        team.score = score_for_team[team]
        team.save()
