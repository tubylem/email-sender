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

### Usage
The configuration of your email server is placed in config.ini file.

```
./main.py \
  --from "sender@example.com" \
  --to "receiver@example.com" \
  --subject "Test" \
  --body "<h1>test message</h1>" \
  --body_type html \
  --attachments test.txt \
  --certificates server.crt
  --password "XXXXXX"
```

