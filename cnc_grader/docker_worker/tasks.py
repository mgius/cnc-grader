import os
import shutil
import tempfile

from celery import shared_task
import docker

from cnc_grader.grader_web import models


@shared_task()
def debug_task(submission_id):
    submission = models.Submission.objects.get(id=submission_id)
    inputs_dir = tempfile.mkdtemp()
    outputs_dir = tempfile.mkdtemp()
    submission_dir = tempfile.mkdtemp()
    c = docker.Client()
    result = 1
    try:
        for testcase in submission.problem.testcase_set.all():
            infile = os.path.join(inputs_dir, 'in%d' % testcase.id)
            outfile = os.path.join(outputs_dir, 'out%d' % testcase.id)
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
            volumes=['/inputs/', '/outputs', '/submission'])
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
