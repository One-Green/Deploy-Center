import subprocess


def run_process(exe):
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        r = p.poll()
        line = p.stdout.readline()
        yield line
        if r is not None:
            break
