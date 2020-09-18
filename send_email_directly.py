'''
Send an email directly without using a relay server
(it's not a script, just the code)

Note: Many servers will reject emails from unknown IPs (gmail seems to accept them, but will mark them as spam)

Author: Eli Finkel - eyfinkel@gmail.com
'''

import socket
EOL = b'\r\n'

to = b'addr@gmail.com'
server = 'alt3.gmail-smtp-in.l.google.com' # Get the server address by running 'nslookup -querytype=MX gmail.com'

s=socket.create_connection((server, 25))

def send(data):
    data += EOL
    s.send(data)
    print('SEND: ' + str(data))
    recv()

def recv():
    print('RECV: ' + str(s.recv(1000)))


recv()
send(b'HELO ' + to.split(b'@')[1])
send(b'MAIL FROM:<guy@site.net>')
send(b'RCPT TO:<'+to+b'>')
send(b'DATA')
send(b'Subject: sub' + EOL +\
     b'From: Eli Sender <sender@send.com>' + EOL +\
     b'To: Eli Recv <recv@recv.com>' + EOL +\
     b'Here\'s my data' + EOL + b'.')
send(b'QUIT')

s.close()
