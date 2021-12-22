#!/usr/bin/env python

import mail_client
import common
import credentials
import time

SYSTMED_SERVICE_NAME = "rpi_remote_mqtt.service"

if __name__ == "__main__":
    while True:
        try:
            m = mail_client.Mail(gmail_user=credentials.mail_user, gmail_pass=credentials.mail_pass)
            cmds = m.get_data_for_topic(credentials.project)
            print(cmds)
            for cmd in cmds:
                if cmd.msg == "reset":
                    common.run_bash_cmd("systemctl --user restart %s" % (SYSTMED_SERVICE_NAME))
                else:
                    print("not implemented %s" % (cmd))
            m = None
        except Exception as e:
            print("Cant read with error %e" % (e))
        time.sleep(60)
