#!/usr/bin/env python3

import time
import os
import shutil
import select
import pty
from subprocess import Popen
from getpass import getpass
import re
import sys

password = None


def get_millis():
    return round(time.time() * 1000)


def millis_passed(timestamp):
    return get_millis() - timestamp


def run_bash_cmd(cmd, echo=False, interaction={}, return_lines=True, return_code=False, cr_as_newline=False):
    if echo: print("CMD:", cmd)
    master_fd, slave_fd = pty.openpty()
    line = ""
    lines = []
    with Popen(cmd, shell=True, preexec_fn=os.setsid, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
               universal_newlines=True) as p:
        while p.poll() is None:
            r, w, e = select.select([sys.stdin, master_fd], [], [], 0.01)
            if master_fd in r:
                o = os.read(master_fd, 10240).decode("UTF-8")
                if o:
                    for c in o:
                        if cr_as_newline and c == "\r":
                            c = "\n"
                        if c == "\n":
                            if line and line not in interaction.values():
                                clean = line.strip().split('\r')[-1]
                                lines.append(clean)
                                if echo: print("STD:", line)
                            line = ""
                        else:
                            line += c
            if line:  # pass password to prompt
                for key in interaction:
                    if key in line:
                        if echo: print("PMT:", line)
                        time.sleep(1)
                        os.write(master_fd, ("%s" % (interaction[key])).encode())
                        os.write(master_fd, "\r\n".encode())
                        line = ""
        if line:
            clean = line.strip().split('\r')[-1]
            lines.append(clean)

    os.close(master_fd)
    os.close(slave_fd)

    if return_lines and return_code:
        return lines, p.returncode
    elif return_code:
        return p.returncode
    else:
        return lines


def get_full_path(path):
    return os.path.realpath(os.path.expanduser(path))


def write_lines_to_file(lines, filename):
    filename = get_full_path(filename)
    with open(filename, 'w') as f:
        f.write("\n".join(lines))


def read_lines_from_file(filename):
    filename = get_full_path(filename)
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    return lines


def check_if_path_exists(path):
    return os.path.exists(get_full_path(path))


def create_path(path):
    os.makedirs(get_full_path(path), exist_ok=True)


def remove_path(path):
    if check_if_path_exists(path):
        shutil.rmtree(get_full_path(path))


def get_file_list_in_path(path, recursive=False, pattern=None):
    list = []
    if recursive:
        list = [os.path.join(dp, f) for dp, dn, fn in os.walk(get_full_path(path)) for f in fn]
    else:
        list = os.listdir(get_full_path(path))
    if pattern:
        list = [l for l in list if re.match(pattern, l)]
    return list


def get_linux_password():
    global password
    if not password:
        password = getpass("Enter [sudo] password: ")
    return password
