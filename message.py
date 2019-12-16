#!/usr/bin/env python3

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class Message:
    def __init__(self):   
        self._create_message()
        
    def _create_message(self):
        """Create the multipart message"""
        self.msg = MIMEMultipart()
        self.sender = None
        self.recipients = []
        self.subject = ""
        
    def set_sender(self, sender):
        """Set sender for a message"""
        self.sender = sender
        
    def set_recipients(self, recipients):
        """Set recipients for a message"""
        self.recipients = recipients
        
    def set_subject(self, subject):
        """Set the subject for a message"""
        self.subject = subject
        
    def set_body(self, text, type="plain"):
        """Attach message text as first attachment"""
        self.msg.attach(MIMEText(text, type))

    def add_attachment(self, file):
        """Add attachment to the message"""
        data = open(file, "rb").read()
        filename = os.path.basename(file)
        part = MIMEBase("application", "octet-stream")
        part.set_payload(data)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=""{}""".format(filename))
        self.msg.attach(part)
        