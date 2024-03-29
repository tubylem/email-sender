#!/usr/bin/env python3

from emailsender import EmailSender
from message import Message
from argparse import ArgumentParser
from configparser import ConfigParser

def main():
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
    
    msg = Message()
    msg.set_sender(args.from_address)
    msg.set_recipients(args.to_addresses)
    msg.set_subject(args.subject)
    msg.set_body(args.body, type=args.body_type)
    
    for attachment in args.attachments:
        msg.add_attachment(attachment)
    
    message = email.set_message(msg, certificates=args.certificates)
    
    print(message)
                             
    email.send(message, 
               password=args.password
              )

if __name__ == "__main__":
    main()
    