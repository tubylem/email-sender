#!/usr/bin/env python3

from M2Crypto import BIO, Rand, SMIME, X509
import smtplib


class EmailSender:
    def __init__(self, host="localhost", port=25, key=None, cert=None, sign=False, encrypt=False, cipher="aes_256_cbc"):
        self.host = host
        self.port = port
        self.key = key
        self.cert = cert
        self.sign = sign
        self.encrypt = encrypt
        self.cipher = cipher
        
    def set_message(self, message, certificates=[]):
        """Sign and encrypt the email and prepare it to send"""
        self.message = message
        # Seed the PRNG.
        Rand.load_file('randpool.dat', -1)
    
        smime = SMIME.SMIME()
        
        # put message with attachments into into SSL" I/O buffer
        msg_str = self.message.msg.as_string()
        msg_bio = BIO.MemoryBuffer(bytes(msg_str, 'utf-8'))
        
        if self.sign:
            smime.load_key(self.key, self.cert)
            p7 = smime.sign(msg_bio, SMIME.PKCS7_DETACHED)
            # Recreate the message because sign function has consumed it
            msg_bio = BIO.MemoryBuffer(bytes(msg_str, 'utf-8')) 

        if self.encrypt:
            sk = X509.X509_Stack()
            for cert in certificates:
                sk.push(X509.load_cert(cert))
            smime.set_x509_stack(sk)
            smime.set_cipher(SMIME.Cipher(self.cipher))
            tmp_bio = BIO.MemoryBuffer()
            if self.sign:
                smime.write(tmp_bio, p7, msg_bio)
            else:
                tmp_bio.write(msg_str)
            p7 = smime.encrypt(tmp_bio)

        out = BIO.MemoryBuffer()
        out.write('From: %s\r\n' % self.message.sender)
        out.write('To: %s\r\n' % ", ".join(self.message.recipients))
        out.write('Subject: %s\r\n' % self.message.subject) 
        
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
        
    def send(self, raw_message, password=None): 
        """Send the email"""
        # Connect to the SMTP server
        smtp = smtplib.SMTP(self.host, self.port)
        smtp.ehlo()
        smtp.starttls()
        # Authenticate the user if needed
        if password:
            smtp.login(self.message.sender, password)
        smtp.sendmail(self.message.sender, self.message.recipients, raw_message)
        smtp.quit()
