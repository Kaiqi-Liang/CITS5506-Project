import socket
import datetime
import threading

datetimes: list[datetime.datetime] = []

def server():
	print('Server is running')
	while True:
		conn, _ = server_socket.accept()
		date = conn.recv(100)
		try:
			datetimes.append(datetime.datetime.strptime(date.decode(), '%Y-%m-%d %w %H:%M:%S') )
		except:
			print('The doorbell did not send a valid date')
		with open('out.wav', 'wb') as recording:
			while True:
				try:
					data = conn.recv(1000000)
				except:
					conn.close()
					print('The doorbell disconnected')
					break
				if not data:
					conn.close()
					print('No more data')
					break
				print(len(data))
				recording.write(data)
 
if __name__ == '__main__':
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server_socket.bind(('', 9000))
		server_socket.listen(1)
		server_thread = threading.Thread(name="server", target=server)
		server_thread.start()
	except:
		print('Failed to start the server')
		server_socket.close()
		exit(1)
	while True:
		if (input() == 'unlock'):
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				client_socket.connect(('172.20.10.5', 8000))
				client_socket.send(b'unlock')
				print(client_socket.recv(6))
			except:
				print('Failed to talk to the doorbell')
				client_socket.close()
