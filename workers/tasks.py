from subprocess import Popen, PIPE

from worker import worker


@worker.task
def run_agent():
    with Popen(["ls", "-l"], stdout=PIPE, shell=True) as proc:
        output = proc.stdout.read()

    return output.decode()
