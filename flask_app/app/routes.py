from flask import render_template
from app import app
import socket

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/unlock')
def unlock():
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect(('172.20.10.14', 8000))
		client_socket.send(b'unlock')
		msg = client_socket.recv(6)
	except:
		msg = 'Failed to talk to the doorbell'
		client_socket.close()
	return msg