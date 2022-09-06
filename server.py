import socket
import threading

def server():
	while True:
		try:
			conn, _ = server_socket.accept()
			with open('out.wav', 'wb') as recording:
				while True:
					try:
						data = conn.recv(1000000)
					except:
						print('client disconnected')
						break
					if not data:
						break
					print(len(data))
					recording.write(data)
					try:
						conn.send(b'received')
					except:
						print('client disconnected')
						break
		except:
			conn.close()
 
if __name__ == '__main__':
	try:
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind(('', 8888))
		server_socket.listen(5)
		server_thread = threading.Thread(name="server", target=server)
		server_thread.start()
	except:
		server_socket.close()
	while True:
		print(input())
