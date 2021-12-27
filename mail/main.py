#!/usr/bin/env python

import threading
import time
import os, sys

import credentials
import mail_client

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common.thread_monitor import ThreadMonitor, ThreadMonitorExitStrategySystemdWatchdog
from common.common import run_bash_cmd
from common import log
from mqtt.make import SYSTMED_SERVICE_NAME

logger = log.get()


def main_loop():
    while True:
        try:
            m = mail_client.Mail(gmail_user=credentials.mail_user, gmail_pass=credentials.mail_pass)
            cmds = m.get_data_for_topic(credentials.project)
            logger.debug("fetching commands: %s" % str(cmds))
            for cmd in cmds:
                if cmd.msg == "reset":
                    run_bash_cmd("systemctl --user restart %s" % (SYSTMED_SERVICE_NAME), echo=True)
                else:
                    logger.info("not implemented %s" % (cmd))
            m = None
        except Exception as e:
            logger.error("Cant read with error %e" % (e))
        time.sleep(10)


if __name__ == "__main__":
    logger.info("boot start")
    ThreadMonitor.set_exit_strategy(ThreadMonitorExitStrategySystemdWatchdog())
    ThreadMonitor.watch_main_thread()
    main_loop_thread = threading.Thread(target=main_loop)
    main_loop_thread.start()
    ThreadMonitor.watch(main_loop_thread)
    logger.info("boot end")

    ThreadMonitor.join()
