#!/usr/bin/env python3
# @Date    : 2020-09-24
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.2.1

#####################################################################
# pcall@Version : 0.2.1
#####################################################################
import subprocess

if hasattr(subprocess, 'run'):
    __PY_VERSION_MINOR = 5  # 高于3.5
# except AttributeError:
else:
    __PY_VERSION_MINOR = 4  # 低于3.4

def _popen(str_cmd):
    completing_process = subprocess.Popen(str_cmd,
                                shell=True,
                                # stdin=subprocess.DEVNULL,
                                # stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)
    # stdout, stderr = completing_process.communicate()
    return completing_process


def pcall(str_cmd, block=True):
    ''' return a list stdout-lines '''
    if block:
        if __PY_VERSION_MINOR == 5:
            p = subprocess.run(str_cmd,
                                shell=True,
                                check=True,
                                stdout=subprocess.PIPE)
        else:
            p = subprocess.check_call(str_cmd,
                                shell=True)
        stdout = p.stdout
    else:
        p = _popen(str_cmd)
        stdout = p.communicate()  # timeout=timeout
    # rc = p.returncode
    return stdout.decode().splitlines()

#####################################################################
# end of pcall
#####################################################################
