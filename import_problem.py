import argparse
import os

from cnc_grader.grader_web.models import Problem, TestCase


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputsdir', required=True)
    parser.add_argument('--outputsdir', required=True)
    parser.add_argument('--problem-text-file', required=True)
    parser.add_argument('--problem-name', required=True)

    return parser.parse_args()


def create_problem(args):
    problem = Problem(title=args.problem_name,
                      text=open(args.problem_text_file).read())
    problem.save()

    for inputfile in os.listdir(args.inputsdir):
        input = open(os.path.join(args.inputsdir, inputfile)).read()
        output = open(os.path.join(args.outputsdir,
                                   inputfile)).read()
        t = TestCase(problem=problem, input=input, output=output)
        t.save()


def main():
    args = parse_args()
    create_problem(args)


if __name__ == '__main__':
    main()
