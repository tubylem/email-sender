#!/usr/bin/env python3

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from M2Crypto import BIO, Rand, SMIME, X509
from argparse import ArgumentParser
import smtplib, string, sys, os


class EmailSender:
    def __init__(self, host="localhost", port=25, key=None, cert=None, sign=False, encrypt=False):
        self.host = host
        self.port = port
        self.key = key
        self.cert = cert
        self.sign = sign
        self.encrypt = encrypt
        self.cipher = "aes_256_cbc"
        
    def create_message(self, body="", type="plain", attachments=[]):   
        """Create the multipart message with a body and attachments""" 
        # create multipart message
        msg = MIMEMultipart()

        # attach message text as first attachment
        msg.attach(MIMEText(body, type))
        
        # attach files to be read from file system
        for attachment in attachments:
            self.add_attachment(msg, attachment)
        
        return msg

    def add_attachment(self, msg, file):
        """Add attachment to the message"""
        part = MIMEBase("application", "octet-stream")
        part.set_payload(open(file,"rb").read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=""{}""".format(os.path.basename(file)))
        msg.attach(part)
        
    def add_certificates(self, smime, certs):
        """Add certificates to encrypt the message"""
        sk = X509.X509_Stack()
        for x in certs:
            sk.push(X509.load_cert(x))
        smime.set_x509_stack(sk)
        smime.set_cipher(SMIME.Cipher(self.cipher))
        
    def _prepare_email(self, from_address, to_addresses, subject, msg, certs=[]):
        """Sign and encrypt the email and prepare it to send"""
        # Seed the PRNG.
        Rand.load_file('randpool.dat', -1)
    
        smime = SMIME.SMIME()
        
        # put message with attachments into into SSL" I/O buffer
        msg_str = msg.as_string()
        msg_bio = BIO.MemoryBuffer(bytes(msg_str, 'utf-8'))
        
        if self.sign:
            smime.load_key(self.key, self.cert)
            p7 = smime.sign(msg_bio, SMIME.PKCS7_DETACHED)
            msg_bio = BIO.MemoryBuffer(bytes(msg_str, 'utf-8')) # Recreate coz sign() has consumed it.

        if self.encrypt:
            self.add_certificates(smime, certs)
            tmp_bio = BIO.MemoryBuffer()
            if self.sign:
                smime.write(tmp_bio, p7, msg_bio)
            else:
                tmp_bio.write(msg_str)
            p7 = smime.encrypt(tmp_bio)

        out = BIO.MemoryBuffer()
        out.write('From: %s\r\n' % from_address)
        out.write('To: %s\r\n' % ", ".join(to_addresses))
        out.write('Subject: %s\r\n' % subject) 
        
        if self.encrypt:
            smime.write(out, p7)
        elif self.sign:
            smime.write(out, p7, msg_bio)
        else:
            out.write(msg_str)
                
        out.close()
        
        # Save the PRNG's state.
        Rand.save_file('randpool.dat')
        
        return out.read().decode("utf-8")
        
    def send_email(self, from_address, to_addresses, subject, msg, certs=[], password=None): 
        """Send the email and return the message"""
        results = self._prepare_email(from_address, to_addresses, subject, msg, certs=certs)
    
        # Connect to the SMTP server
        smtp = smtplib.SMTP(self.host, self.port)
        smtp.ehlo()
        smtp.starttls()
        # Authenticate the user if needed
        if password:
            smtp.login(from_address, password)
        smtp.sendmail(from_address, to_addresses, results)
        smtp.quit()
        
        return results
