#!/bin/bash
import sys

from src.common import *
import src.log as log
import os, getpass

logger = log.get()

SYSTMED_SERVICE_NAME = "rpi_remote_mqtt.service"
SYSTMED_SERVICE_PATH = get_full_path("./systemd")
SYSTEMD_PATH = get_full_path("~/.config/systemd/user")
root_password = ""


def get_root_password():
    global root_password
    if not root_password:
        root_password = getpass.getpass("Enter [sudo] password: ")
    return root_password


def _create_dir():
    logger.info("[INS]: create_dir %s" % (SYSTEMD_PATH))
    cmd = "mkdir -p %s" % (SYSTEMD_PATH)
    run_bash_cmd(cmd)


def _change_user_and_copy_service():
    logger.info("[INS]: change_user_and_copy_service")
    old_location = "%s/%s" % (SYSTMED_SERVICE_PATH, SYSTMED_SERVICE_NAME)
    user = getpass.getuser()
    new_location = "%s/%s" % (SYSTEMD_PATH, SYSTMED_SERVICE_NAME)
    logger.info("[INS]: for user %s copy from %s to %s" % (user, old_location, new_location))
    lines = read_lines_from_file(old_location)
    for index, line in enumerate(lines):
        if "<USER>" in lines[index]:
            lines[index] = lines[index].replace("<USER>", user)
            print(lines[index])
            break
    write_lines_to_file(lines, new_location)


def _systemd_deamon_reload():
    logger.info("[INS]: systemd_deamon_reload")
    cmd = "systemctl --user daemon-reload"
    run_bash_cmd(cmd)


def start():
    logger.info("[INS]: systemd_service_start")
    cmd = "systemctl --user start %s" % (SYSTMED_SERVICE_NAME)
    run_bash_cmd(cmd)


def stop():
    logger.info("[INS]: systemd_service_stop")
    cmd = "systemctl --user stop %s" % (SYSTMED_SERVICE_NAME)
    run_bash_cmd(cmd)


def restart():
    logger.info("[INS]: systemd_service_restart")
    cmd = "systemctl --user restart %s" % (SYSTMED_SERVICE_NAME)
    run_bash_cmd(cmd)


def enable():
    logger.info("[INS]: systemd_service_enable")
    cmd = "systemctl --user enable %s" % (SYSTMED_SERVICE_NAME)
    run_bash_cmd(cmd)


def log(follow=True, lines_to_show=1000):
    cmd = "journalctl"
    cmd += " -o short-precise"
    cmd += " -n %s" % (lines_to_show)
    cmd += (" -e", " -f")[follow]
    cmd += " --user-unit=%s" % (SYSTMED_SERVICE_NAME)
    cmd = "bash -c '%s'" % (cmd)
    print(cmd)
    os.system(cmd)


def clean_logs():
    cmd = "sudo journalctl --unit %s --vacuum-time=1s" % (SYSTMED_SERVICE_NAME)
    interaction = {"[sudo]": get_root_password()}
    run_bash_cmd(cmd, interaction=interaction)


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    if len(sys.argv) == 2 and sys.argv[1] == "-i":
        logger.info("[INS]: Installing systemd service")
        _create_dir()
        _change_user_and_copy_service()
        _systemd_deamon_reload()
        sys.exit(0)

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
