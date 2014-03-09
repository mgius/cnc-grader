import logging
import os
import subprocess
import sys

MAX_RUN_TIME = 60


class BaseLanguage(object):
    extension = None

    def __init__(self, source_filename):
        self.source_filename = source_filename
        self.compiled_filename = source_filename

    def compile(self):
        pass

    @staticmethod
    def _run_diffed(run_base, inputfile, outputfile):
        # run the command, sourcing stdin from the inputfile and sending stdout
        # and stderr to pipe
        run_cmd = ['timeout', str(MAX_RUN_TIME)] + run_base
        run_cmd = subprocess.Popen(run_cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=open(inputfile),
                                   close_fds=True)

        # whitespace agnostic diff
        diff_cmd = subprocess.Popen(['timeout', str(MAX_RUN_TIME),
                                     '/usr/bin/diff',
                                     '--ignore-all-space',
                                     '--ignore-blank-lines',
                                     '--ignore-space-change',
                                     '-', outputfile],
                                    stdout=open(os.devnull, 'w'),
                                    stdin=run_cmd.stdout)

        run_exit = run_cmd.wait()
        diff_exit = diff_cmd.wait()
        if run_exit != 0 or diff_exit != 0:
            logging.error("Test run of %s failed.\n"
                          "  Execute exit code %d\n"
                          "  Diff exit code %d\n"
                          "  Input file %s",
                          run_base, run_exit, diff_exit, inputfile)
            sys.exit(1)

    def run(self, inputfile, outputfile):
        raise NotImplementedError


class Python(BaseLanguage):
    extension = 'py'

    def run(self, inputfile, outputfile):
        self._run_diffed(['python', self.source_filename],
                         inputfile, outputfile)


Python('/home/mgius/src/cnc-grader/test_problems/ones/ones-bad1.py').run(
    '/home/mgius/src/cnc-grader/test_problems/ones/inputs/in1',
    '/home/mgius/src/cnc-grader/test_problems/ones/outputs/out1')
