import socket

USER_ADDR_INFO = ('192.168.137.162', 9000)
DOORBELL_ADDR_INFO = ('100.90.44.216', 8000)
START_AUDIO = b'start sending audio'
END_AUDIO = b'finish sending audio'
END_IMAGE = b'finish sending image'
UNLOCK_SIGNAL = b'unlock'
RECEIVED_MSG_LEN = 15
DATE_LEN = 100

def data_to_file(conn: socket.socket, filename: str, endswith: bytes, message: bytes):
	with open(filename, 'wb') as file:
		while True:
			data = conn.recv(10000)
			if data.endswith(endswith):
				data = data[:-len(endswith)]
				file.write(data)
				break
			file.write(data)
	conn.send(message)

import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content('hi')

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'hi'
msg['From'] = 'kaiqi.liang@uwa.edu.au'
msg['To'] = 'kaiqi.liang@unsw.edu.au'

# Send the message via our own SMTP server.
s = smtplib.SMTP('localhost', 7000)
s.send_message(msg)
s.quit()