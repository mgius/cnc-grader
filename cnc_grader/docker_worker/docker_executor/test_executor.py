import argparse
import functools
import logging
import os
import subprocess
import sys

MAX_RUN_TIME = 60


class Registry(object):
    def __init__(self):
        self.registry = {}

    def register(self, name, tracked):
        self.registry[name] = tracked
        return tracked

    def __call__(self, name):
        return functools.partial(self.register, name)

    def get(self, name):
        return self.registry[name]


extension = Registry()  # pylint: disable=C0103


def timeout_popen(cmd, timeout=MAX_RUN_TIME, **kwargs):
    cmd = ['timeout', str(timeout)] + cmd
    return subprocess.Popen(cmd, **kwargs)


class BaseLanguage(object):
    def __init__(self, source_filename):
        self.source_filename = source_filename
        self.compiled_filename = source_filename

    def compile(self):
        pass

    @staticmethod
    def _run_diffed(run_base, inputfile, outputfile):
        # run the command, sourcing stdin from the inputfile and sending stdout
        # and stderr to pipe
        run_cmd = timeout_popen(run_base,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=open(inputfile),
                                close_fds=True)

        # whitespace agnostic diff
        diff_cmd = timeout_popen(['/usr/bin/diff',
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


@extension("py")
class Python(BaseLanguage):
    def run(self, inputfile, outputfile):
        self._run_diffed(['python', self.compiled_filename],
                         inputfile, outputfile)


@extension("pl")
class Perl(BaseLanguage):
    def run(self, inputfile, outputfile):
        self._run_diffed(['perl', self.compiled_filename],
                         inputfile, outputfile)


@extension("java")
class Java(BaseLanguage):
    def compile(self):
        compile_command = timeout_popen(['javac', self.source_filename],
                                        timeout=10,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

        compile_exit = compile_command.wait()
        if compile_exit != 0:
            logging.error("Compilation of %s failed\n"
                          "  Stdout: %s\n"
                          "  Stderr: %s\n",
                          self.source_filename,
                          compile_command.stdout.read(),
                          compile_command.stderr.read())
            sys.exit(1)

    def run(self, inputfile, outputfile):
        classpath = os.path.dirname(self.source_filename)
        classname = os.path.basename(self.source_filename).rsplit('.', 1)[0]
        self._run_diffed(['java', '-cp', classpath, classname],
                         inputfile, outputfile)


@extension("c")  # pylint: disable=C0103
class C(BaseLanguage):
    def compile(self):
        self.compiled_filename = self.source_filename.rsplit('.', 1)[0]
        compile_command = timeout_popen(
            ['gcc', '-o', self.compiled_filename, self.source_filename],
            timeout=10)

        compile_exit = compile_command.wait()
        if compile_exit != 0:
            logging.error("Compilation of %s failed\n"
                          "  Stdout: %s\n"
                          "  Stderr: %s\n",
                          self.source_filename,
                          compile_command.stdout.read(),
                          compile_command.stderr.read())
            sys.exit(1)

    def run(self, inputfile, outputfile):
        self._run_diffed([self.compiled_filename], inputfile, outputfile)


@extension("cpp")
class CPP(BaseLanguage):
    def compile(self):
        self.compiled_filename = self.source_filename.rsplit('.', 1)[0]
        compile_command = timeout_popen(
            ['g++', '-o', self.compiled_filename, self.source_filename],
            timeout=10)

        compile_exit = compile_command.wait()
        if compile_exit != 0:
            logging.error("Compilation of %s failed\n"
                          "  Stdout: %s\n"
                          "  Stderr: %s\n",
                          self.source_filename,
                          compile_command.stdout.read(),
                          compile_command.stderr.read())
            sys.exit(1)

    def run(self, inputfile, outputfile):
        self._run_diffed([self.compiled_filename], inputfile, outputfile)


def parse_args():
    def dirtype(obj):
        if not os.path.isdir(obj):
            raise TypeError("%s is not a directory" % obj)

        return obj

    def filetype(obj):
        if not os.path.isfile(obj):
            raise TypeError("%s is not a file" % obj)

        return obj

    argparser = argparse.ArgumentParser()

    argparser.add_argument('--inputsdir', type=dirtype, required=True)
    argparser.add_argument('--outputsdir', type=dirtype, required=True)
    argparser.add_argument('--submission', type=filetype, required=True)

    return argparser.parse_args()


def main():
    args = parse_args()

    file_ext = args.submission.rsplit('.', 1)[1]
    language = extension.get(file_ext)

    if language is None:
        logging.error("Extension %s is not supported", file_ext)
        sys.exit(1)

    language = language(args.submission)
    language.compile()

    for testname in os.listdir(args.inputsdir):
        language.run(os.path.join(args.inputsdir, testname),
                     os.path.join(args.outputsdir, testname))


if __name__ == '__main__':
    main()
