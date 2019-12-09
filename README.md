# email-sender
The program sends signed and encrypted emails

# Requirements to build the program
```
yum install gcc gcc-c++ make openssl-devel python3-devel
```

# Generating certificates
```
openssl req -x509 -nodes -newkey rsa:2048 -keyout server.key -out server.crt -nodes -days 365
openssl pkcs12 -export -out server.pfx -inkey server.key -in server.crt
```

# Usage
```
./EmailSender.py --from "sender@example.com" --to "receiver@example.com" --subject "Test" --body "<h1>test message</h1>" --body_type html --attachments test.txt --certificates server.crt
```