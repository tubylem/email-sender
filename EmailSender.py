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
        
    def createMessage(self, body="", type="plain", attachments=[]):        
        # create multipart message
        msg = MIMEMultipart()

        # attach message text as first attachment
        msg.attach(MIMEText(body, type))
        
        # attach files to be read from file system
        for attachment in attachments:
            self.addAttachment(msg, attachment)
        
        return msg

    def addAttachments(self, msg, file):
        part = MIMEBase("application", "octet-stream")
        part.set_payload(open(file,"rb").read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=""{}""".format(os.path.basename(file)))
        msg.attach(part)
        
    def addCertificates(self, smime, certs):
        sk = X509.X509_Stack()
        for x in certs:
            sk.push(X509.load_cert(x))
        smime.set_x509_stack(sk)
        smime.set_cipher(SMIME.Cipher("aes_256_cbc"))
        
    def prepareEmail(self, from_address, to_addresses, subject, msg, certs=[]):
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
            sk = X509.X509_Stack()
            for x in certs:
                sk.push(X509.load_cert(x))
            smime.set_x509_stack(sk)
            smime.set_cipher(SMIME.Cipher('aes_256_cbc'))
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
        
    def sendEmail(self, from_address, to_addresses, subject, msg, certs=[], password=None):  
        results = self.prepareEmail(from_address, to_addresses, subject, msg, certs=certs)
    
        smtp = smtplib.SMTP(self.host, self.port)
        smtp.ehlo()
        smtp.starttls()
        if password:
            smtp.login(from_address, password)
        smtp.sendmail(from_address, to_addresses, results)
        smtp.quit()
        
        return results

from argparse import ArgumentParser
from configparser import ConfigParser

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('--from_address', required=True, help="sender email address")
    parser.add_argument('--to_addresses', required=True, nargs='+', help="list of receivers email addresses")
    parser.add_argument('--subject', required=True, help="subject")
    parser.add_argument('--body', required=True, help="message body")
    parser.add_argument('--body_type', choices=['plain', 'html'], default='plain', help="message body type (default: %(default)s)")
    parser.add_argument('--attachments', nargs='*', help="list of attachments")
    parser.add_argument('--certificates', nargs='*', help="list of certificates")
    parser.add_argument('--config', default="config.ini", help="config file location")
    parser.add_argument('--password', help="password for email server authentication")
    
    args = parser.parse_args()
    
    conf_parser = ConfigParser({'host': 'localhost', 'port': 25, 'sign': False, 'Encrypt': False})
    conf_args = conf_parser.read(args.config)
    
    if len(conf_args) != 1:
        raise FileNotFoundError("The config file does not exist")
    
    email = EmailSender(host=conf_parser.get('mail', 'host'), 
                        port=conf_parser.getint('mail', 'port'), 
                        key=conf_parser.get('mail', 'key'), 
                        cert=conf_parser.get('mail', 'cert'), 
                        sign=conf_parser.getboolean('mail', 'sign'), 
                        encrypt=conf_parser.getboolean('mail', 'encrypt')
                       )
    
    msg = email.createMessage(body=args.body, 
                              type=args.body_type, 
                              attachments=args.attachments
                             )
                             
    results = email.sendEmail(args.from_address, 
                              args.to_addresses, 
                              args.subject, 
                              msg, 
                              certs=args.certificates, 
                              password=args.password
                             )
    print(results)
    