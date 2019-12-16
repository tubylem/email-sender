# email-sender
The program sends signed and encrypted emails.

### Requirements to install m2crypto
```
yum install gcc gcc-c++ make openssl-devel python3-devel
```

### Generating certificates
```
openssl req -x509 -nodes -newkey rsa:2048 -keyout server.key -out server.crt -nodes -days 365
openssl pkcs12 -export -out server.pfx -inkey server.key -in server.crt
```

### Simple example
```
from emailsender import EmailSender
from message import Message

msg = Message()
msg.set_sender("sender@example.com")
msg.set_recipients(["recipient@example.com"])
msg.set_subject("Test")
msg.set_body("<h1>Test message</h1>", type="html")
    
email = EmailSender(host="localhost", port=25)
raw_message = email.set_message(msg)
print(raw_message)
                             
email.send(raw_message)
```

### Sign & Encrypt example
```
from emailsender import EmailSender
from message import Message

msg = Message()
msg.set_sender("sender@example.com")
msg.set_recipients(["recipient@example.com"])
msg.set_subject("Test")
msg.set_body("<h1>Test message</h1>", type="html")
    
email = EmailSender(host="localhost", port=25, sign=True, encrypt=True, key="server.key", cert="server.pem")
raw_message = email.set_message(msg, certificates=["cert1.pem", "cert2.pem"])
print(raw_message)
                             
email.send(raw_message)
```

### Usage
The configuration of your email server is placed in config.ini file.

```
python main.py \
  --from "sender@example.com" \
  --to "receiver@example.com" \
  --subject "Test" \
  --body "<h1>test message</h1>" \
  --body_type html \
  --attachments test.txt \
  --certificates server.crt
  --password "XXXXXX"
```

