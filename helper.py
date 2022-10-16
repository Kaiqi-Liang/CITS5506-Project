import socket
import sys

IP_ADDRESS = '127.0.0.1'
# Get the ip address from the commandline argument
try:
	IP_ADDRESS = sys.argv[1]
except:
	print('Usage: python user.py | doorbell.py ip_address')
	print('Did not provide an IP address, using localhost as default')

DOORBELL_ADDR_INFO = (IP_ADDRESS, 8000)
USER_ADDR_INFO = (IP_ADDRESS, 9000)
UNLOCK_SIGNAL = b'unlock'
START_AUDIO = b'start sending audio'
END_AUDIO = b'finish sending audio'
END_IMAGE = b'finish sending image'
RECEIVED_AUDIO = b'received audio'
RECEIVED_IMAGE = b'received image'
RECEIVED_MSG_LEN = 15
DATE_LEN = 100

def data_to_file(conn: socket.socket, filename: str, endswith: bytes, message: bytes):
	'''
	Receive a stream of data and write them to a file
	'''
	with open(filename, 'wb') as file:
		while True:
			data = conn.recv(10000)
			if data.endswith(endswith):
				data = data[:-len(endswith)]
				file.write(data)
				break
			file.write(data)
	conn.send(message)
