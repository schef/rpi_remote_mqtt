#!/bin/bash
import sys

from src.common import *
import src.log as log
import os, getpass

logger = log.get()

SYSTMED_SERVICE_NAME = "rpi_remote_mqtt.service"
SYSTMED_SERVICE_PATH = get_full_path("./systemd")
SYSTEMD_PATH = get_full_path("~/.config/systemd/user")


def create_dir():
    logger.info("[INS]: create_dir %s" % (SYSTEMD_PATH))
    cmd = "mkdir -p %s" % (SYSTEMD_PATH)
    run_bash_cmd(cmd)


def change_user_and_copy_service():
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


def systemd_deamon_reload():
    logger.info("[INS]: systemd_deamon_reload")
    cmd = "systemctl --user daemon-reload"
    run_bash_cmd(cmd)


def systemd_service_start():
    logger.info("[INS]: systemd_service_start")
    cmd = "systemctl --user start %s" % (SYSTMED_SERVICE_NAME)
    run_bash_cmd(cmd)


def systemd_service_stop():
    logger.info("[INS]: systemd_service_stop")
    cmd = "systemctl --user stop %s" % (SYSTMED_SERVICE_NAME)
    run_bash_cmd(cmd)


def systemd_service_restart():
    logger.info("[INS]: systemd_service_restart")
    cmd = "systemctl --user restart %s" % (SYSTMED_SERVICE_NAME)
    run_bash_cmd(cmd)


def systemd_service_enable():
    logger.info("[INS]: systemd_service_enable")
    cmd = "systemctl --user enable %s" % (SYSTMED_SERVICE_NAME)
    run_bash_cmd(cmd)


def systemd_log(follow=True, lines_to_show=1000):
    cmd = "journalctl"
    cmd += " -o short-precise"
    cmd += " -n %s" % (lines_to_show)
    cmd += (" -e", " -f")[follow]
    cmd += " --user-unit=%s" % (SYSTMED_SERVICE_NAME)
    cmd = "bash -c '%s'" % (cmd)
    print(cmd)
    os.system(cmd)


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    if len(sys.argv) == 2 and sys.argv[1] == "-i":
        logger.info("[INS]: Installing systemd service")
        create_dir()
        change_user_and_copy_service()
        systemd_deamon_reload()
        sys.exit(0)

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
