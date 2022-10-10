from helper import DOORBELL_ADDR_INFO, USER_ADDR_INFO, START_AUDIO, END_AUDIO, END_IMAGE, UNLOCK_SIGNAL, RECEIVED_MSG_LEN, DATE_LEN, data_to_file
import os
import socket
import datetime
import threading
import signal
import flask
import yaml
import plot

APP = flask.Flask(__name__)
DATETIMES: list[datetime.datetime] = []
UPDATE = False
ERROR_MESSAGE = 'Failed to establish a connection with the doorbell'
USERNAME = 'username'
PASSWORD = 'password'

@APP.after_request
def add_header(response):
	'''
	Add headers to disable browser caching
	'''
	response.headers['Pragma'] = 'no-cache'
	response.headers['Cache-Control'] = 'no-cache, no-store'
	return response

@APP.route('/')
def index():
	return flask.render_template('index.html')

@APP.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return flask.render_template('login.html')

	if flask.request.form.get('username') != USERNAME or flask.request.form.get('password') != PASSWORD:
		return 'Invalid username or password', 403
	return {}

@APP.route('/edit')
def edit():
	username = flask.request.args.get('username')
	password = flask.request.args.get('password')
	global USERNAME
	global PASSWORD
	if USERNAME == username and PASSWORD == password:
		return 'Same username and password', 400
	USERNAME = username
	PASSWORD = password
	return {}

@APP.route('/poll')
def poll():
	'''
	Allow frontend to poll for updates
	'''
	global UPDATE
	if UPDATE:
		# Reset the flag after the frontend has received the update
		UPDATE = False
		return str(True)
	return str(UPDATE)

@APP.route('/unlock')
def unlock():
	'''
	Send a message to the doorbell to unlock the door
	'''
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect(DOORBELL_ADDR_INFO)
		client_socket.send(UNLOCK_SIGNAL)
		print(client_socket.recv(6)) # b'locked'
		return {}
	except:
		print(ERROR_MESSAGE)
		client_socket.close()
		return ERROR_MESSAGE, 500

@APP.route('/audio', methods=['POST'])
def audio():
	'''
	Send a recording to the doorbell
	'''
	# Convert audio data to a wav file
	files = flask.request.files
	audio = files.get('audio')
	audio.save('static/assets/out.wav')

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect(DOORBELL_ADDR_INFO)
		client_socket.send(START_AUDIO)
		with open('static/assets/out.wav', 'rb') as audio:
			for chunk in audio:
				client_socket.send(chunk)
		client_socket.send(END_AUDIO)
		print(client_socket.recv(RECEIVED_MSG_LEN)) # b'received audio'
		return {}
	except:
		print(ERROR_MESSAGE)
		client_socket.close()
		return ERROR_MESSAGE, 500

def server():
	'''
	Server code to receive data from the doorbell
	including a datetime object when the doorbell is pressed,
	an image taken at the door and
	an audio recording
	'''
	while True:
		conn, _ = server_socket.accept()
		while True:
			try:
				date = conn.recv(DATE_LEN)
				try:
					# Add a datetime object to the database
					date = datetime.datetime.strptime(date.decode(), '%Y-%m-%d %w %H:%M:%S')
					print(date)
					DATETIMES.append(date)
					with open('datetimes.yml', 'w') as file:
						yaml.dump(DATETIMES, file)
					plot.plot(DATETIMES)
					conn.send(b'received date')
				except:
					conn.send(b'invalid date')

				# Receive the image and audio data and write to files
				data_to_file(conn, 'static/assets/in.jpeg', END_IMAGE, b'received image')
				data_to_file(conn, 'static/assets/in.wav', END_AUDIO, b'received audio')

				# Set the flag so the frontend can receive an update
				global UPDATE
				UPDATE = True
			except:
				conn.close()
				print('Lost connection with the doorbell')
				break

if __name__ == '__main__':
	# Read in the database which stores all the datetimes when the doorbell was pressed
	if not os.path.isfile('datetimes.yml'):
		open('datetimes.yml', 'w')
	with open('datetimes.yml', 'r') as file:
		DATETIMES = yaml.full_load(file)

	# Start a server on a different thread to listen for requests from the doorbell
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server_socket.bind(('', USER_ADDR_INFO[1]))
		# Only allows 1 connection at a time
		server_socket.listen(1)
		threading.Thread(target=server).start()
		print(f'Server is listening on port {USER_ADDR_INFO[1]}')
	except Exception as error:
		print(f'Failed to start the server: {error}')
		server_socket.close()
		exit(1)

	# Run the Flask server on a different thread
	threading.Thread(target=lambda: APP.run(use_reloader=False)).start()

	# Close the socket when Control-C is pressed to end the program
	def handler(*_):
		exit(0)

	signal.signal(signal.SIGINT, handler)
