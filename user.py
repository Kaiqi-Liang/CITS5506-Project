import socket
import datetime
import threading
import flask

APP = flask.Flask(__name__)

@APP.route('/')
def index():
	return flask.render_template('index.html')

@APP.route('/unlock')
def unlock():
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect(('100.90.44.216', 8000))
		client_socket.send(b'unlock')
		print(client_socket.recv(6))
	except:
		print('Failed to talk to the doorbell')
		client_socket.close()


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

		# receive images
		with open('out.jpeg', 'wb') as image:
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
				image.write(data)

		# receive audio
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
		server_socket.bind(('', 9005))
		server_socket.listen(1)
		server_thread = threading.Thread(name="server", target=server)
		server_thread.start()
	except:
		print('Failed to start the server')
		server_socket.close()
		exit(1)
	backend_thread = threading.Thread(name="backend", target=lambda: APP.run(debug=True, port=5000, use_reloader=False))
	backend_thread.start()
