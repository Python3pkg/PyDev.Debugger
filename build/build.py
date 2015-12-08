from __future__ import print_function

import os
import struct
import itertools
import subprocess
import sys


def validate_pair(ob):
    try:
        if not (len(ob) == 2):
            print("Unexpected result:", ob, file=sys.stderr)
            raise ValueError
    except:
        return False
    return True


def consume(it):
    try:
        while True:
            next(it)
    except StopIteration:
        pass

def get_environment_from_batch_command(env_cmd, initial=None):
    """
    Take a command (either a single command or list of arguments)
    and return the environment created after running that command.
    Note that if the command must be a batch file or .cmd file, or the
    changes to the environment will not be captured.

    If initial is supplied, it is used as the initial environment passed
    to the child process.
    """
    if not isinstance(env_cmd, (list, tuple)):
        env_cmd = [env_cmd]
    # construct the command that will alter the environment
    env_cmd = subprocess.list2cmdline(env_cmd)
    # create a tag so we can tell in the output when the proc is done
    tag = 'Done running command'
    # construct a cmd.exe command to do accomplish this
    cmd = 'cmd.exe /s /c "{env_cmd} && echo "{tag}" && set"'.format(**vars())
    # launch the process
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=initial)
    # parse the output sent to stdout
    lines = proc.stdout
    # consume whatever output occurs until the tag is reached
    consume(itertools.takewhile(lambda l: tag not in l, lines))
    # define a way to handle each KEY=VALUE line
    handle_line = lambda l: l.rstrip().split('=', 1)
    # parse key/values into pairs
    pairs = map(handle_line, lines)
    # make sure the pairs are valid
    valid_pairs = filter(validate_pair, pairs)
    # construct a dictionary of the pairs
    result = dict(valid_pairs)
    # let the process finish
    proc.communicate()
    return result


def is_python_64bit():
    return (struct.calcsize('P') == 8)

def build():
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))

    if sys.platform == 'win32':

        # "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat"
        # set MSSdk=1
        # set DISTUTILS_USE_SDK=1
        # set VS90COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\Tools

        if is_python_64bit():
            env = get_environment_from_batch_command(
                r"""C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat""",
                initial=os.environ.copy())
        else:
            env = get_environment_from_batch_command(
                r"""C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars32.bat""",
                initial=os.environ.copy())
        env['MSSdk'] = '1'
        env['DISTUTILS_USE_SDK'] = '1'
        env['VS90COMNTOOLS'] = r'C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\Tools'

    subprocess.check_call([
        sys.executable, os.path.join(os.path.dirname(__file__), '..', 'setup_cython.py'),
        'build_ext', '--inplace', ], env=env,)

if __name__ == '__main__':
    build()