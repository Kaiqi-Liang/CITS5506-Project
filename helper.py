import socket
import sys

# Get the ip address from the commandline argument
try:
	IP_ADDRESS = sys.argv[1]
except:
	print('Usage: python user.py | doorbell.py ip_address')
	exit(1)

USER_ADDR_INFO = (IP_ADDRESS, 9000)
DOORBELL_ADDR_INFO = (IP_ADDRESS, 8000)
START_AUDIO = b'start sending audio'
END_AUDIO = b'finish sending audio'
END_IMAGE = b'finish sending image'
UNLOCK_SIGNAL = b'unlock'
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
