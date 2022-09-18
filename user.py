import socket
import datetime
import threading
import flask
import plot

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
	return {}

@APP.route('/sendaudio', methods=['POST'])
def send_audio():
	files = flask.request.files
	audio = files.get('audio')
	audio.save('static/out.wav')

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect(('100.90.44.216', 8000))
		client_socket.send(b'start sending audio')
		with open('static/out.wav', 'rb') as recording:
			for chunk in recording:
				client_socket.send(chunk)
		client_socket.send(b'finished sending audio')
		print(client_socket.recv(15))
	except:
		print('Failed to talk to the doorbell')
		client_socket.close()
	return {}

datetimes: list[datetime.datetime] = []

def server():
	print('Server is running')
	while True:
		conn, _ = server_socket.accept()
		while True:
			try:
				date = conn.recv(100)
				try:
					datetimes.append(datetime.datetime.strptime(date.decode(), '%Y-%m-%d %w %H:%M:%S') )
					plot.plot(datetimes)
				except:
					print('The doorbell did not send a valid date')
				conn.send(b'received date')

				# receive image
				with open('static/in.jpeg', 'wb') as image:
					while True:
						data = conn.recv(10000)
						FINISHED_SENDING_IMAGE = b'finished sending image'
						if data.endswith(FINISHED_SENDING_IMAGE):
							data = data[:-len(FINISHED_SENDING_IMAGE)]
							image.write(data)
							break
						image.write(data)
				conn.send(b'received image')

				# receive audio
				with open('static/in.wav', 'wb') as recording:
					while True:
						data = conn.recv(10000)
						if data.endswith(b'finished sending audio'):
							break
						recording.write(data)
				conn.send(b'received audio')
			except:
				conn.close()
				print('Lost connection with the doorbell')
				break
 
if __name__ == '__main__':
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server_socket.bind(('', 9001))
		server_socket.listen(1)
		threading.Thread(target=server).start()
	except:
		print('Failed to start the server')
		server_socket.close()
		exit(1)
	threading.Thread(target=lambda: APP.run(use_reloader=False)).start()
