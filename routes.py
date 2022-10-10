from helper import DOORBELL_ADDR_INFO, START_AUDIO, END_AUDIO, UNLOCK_SIGNAL, RECEIVED_MSG_LEN
import flask
import socket

APP = flask.Flask(__name__)
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
	'''
	Return the home page
	'''
	return flask.render_template('index.html')

@APP.route('/login', methods=['GET', 'POST'])
def login():
	'''
	Return the login page if receives a get request otherwise validate the username and password
	'''
	if flask.request.method == 'GET':
		return flask.render_template('login.html')

	if flask.request.form.get('username') != USERNAME or flask.request.form.get('password') != PASSWORD:
		return 'Invalid username or password', 403
	return {}

@APP.route('/edit')
def edit():
	'''
	Edit username and password
	'''
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
