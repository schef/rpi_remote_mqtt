from email import message_from_bytes, message_from_string
from email.header import decode_header, make_header
from imaplib import IMAP4_SSL
import re


class Mail:
    def __init__(self, gmail_user: str, gmail_pass: str):
        self.mail = IMAP4_SSL('imap.gmail.com')  # connects to gmail using imaplib
        try:
            self.mail.login(user=gmail_user, password=gmail_pass)  # login to your gmail account using the env variables
            self.mail.list()  # list all the folders within your mailbox (like inbox, sent, drafts, etc)
            self.mail.select('inbox')  # selects inbox from the list
        except Exception:
            self.mail = None
        self.username = gmail_user

    def __del__(self):
        if self.mail:
            self.mail.close()
            self.mail.logout()

    class Message:
        def __init__(self, sender, sub, msg):
            self.sender = sender
            self.sub = sub
            self.msg = msg

        def __repr__(self):
            return "[%s,%s,%s]" % (self.sender, self.sub, self.msg)

    def mark_mail_as_unread(self, uid):
        self.mail.store(uid, '-FLAGS', '\\Seen')

    def get_list_of_unread_uids(self):
        return_code, messages = self.mail.search(None, 'UNSEEN')
        if return_code == "OK":
            return messages[0].split()
        return None

    def get_uid_data(self, uid):
        return_code, data = self.mail.fetch(uid, '(RFC822)')
        if return_code == "OK":
            for response_part in data:
                if isinstance(response_part, tuple):
                    original_email = message_from_bytes(response_part[1])
                    raw_email = data[0][1]
                    raw_email_string = raw_email.decode('utf-8')
                    email_message = message_from_string(raw_email_string)
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True)
                            sender = make_header(decode_header((re.split('<|>', original_email['From'])[1])))
                            sub = make_header(decode_header(original_email['Subject'])) if original_email['Subject'] else None
                            msg = (body.decode('utf-8')).strip()
                            return self.Message(sender, sub, msg)
        return None

    def get_data_for_topic(self, topic):
        data = []
        uids = self.get_list_of_unread_uids()
        for uid in uids:
            m = self.get_uid_data(uid)
            if m.sub == topic:
                data.append(m)
            else:
                self.mark_mail_as_unread(uid)
        return data


if __name__ == "__main__":
    # mail = Mail(gmail_user=credentials.mail_user, gmail_pass=credentials.mail_pass)
    pass
