from helper import DOORBELL_ADDR_INFO, START_AUDIO, END_AUDIO, END_IMAGE, UNLOCK_SIGNAL, USER_ADDR_INFO, RECEIVED_MSG_LEN, DATE_LEN, data_to_file
import socket
import datetime
import threading
import flask
import yaml
import plot

APP = flask.Flask(__name__)
DATETIMES: list[datetime.datetime] = []
UPDATE = False

@APP.route('/')
def index():
	return flask.render_template('index.html')

@APP.route('/poll')
def poll():
	global UPDATE
	if UPDATE:
		UPDATE = False
		return str(True)
	return str(UPDATE)

@APP.route('/unlock')
def unlock():
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect(DOORBELL_ADDR_INFO)
		client_socket.send(UNLOCK_SIGNAL)
		print(client_socket.recv(6)) # b'locked'
	except:
		print('Failed to talk to the doorbell')
		client_socket.close()
	return {}

@APP.route('/audio', methods=['POST'])
def audio():
	files = flask.request.files
	audio = files.get('audio')
	audio.save('static/out.wav')

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect(DOORBELL_ADDR_INFO)
		client_socket.send(START_AUDIO)
		with open('static/out.wav', 'rb') as audio:
			for chunk in audio:
				client_socket.send(chunk)
		client_socket.send(END_AUDIO)
		print(client_socket.recv(RECEIVED_MSG_LEN)) # b'received audio'
	except:
		print('Failed to establish a connection with the doorbell')
		client_socket.close()
	return {}

def server():
	print('Server is running')
	while True:
		conn, _ = server_socket.accept()
		while True:
			try:
				date = conn.recv(DATE_LEN)
				try:
					DATETIMES.append(datetime.datetime.strptime(date.decode(), '%Y-%m-%d %w %H:%M:%S') )
					with open('datetimes.yml', 'w') as file:
						yaml.dump(DATETIMES, file)
					plot.plot(DATETIMES)
					conn.send(b'received date')
				except:
					conn.send(b'invalid date')
				data_to_file(conn, 'static/in.jpeg', END_IMAGE, b'received image')
				data_to_file(conn, 'static/in.wav', END_AUDIO, b'received audio')
				global UPDATE
				UPDATE = True
			except:
				conn.close()
				print('Lost connection with the doorbell')
				break
 
if __name__ == '__main__':
	with open('datetimes.yml', 'r') as file:
		DATETIMES = yaml.full_load(file)
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server_socket.bind(('', USER_ADDR_INFO[1]))
		server_socket.listen(1)
		threading.Thread(target=server).start()
	except:
		print('Failed to start the server')
		server_socket.close()
		exit(1)
	threading.Thread(target=lambda: APP.run(use_reloader=False)).start()
