from helper import DOORBELL_ADDR_INFO, USER_ADDR_INFO, START_AUDIO, END_AUDIO, END_IMAGE, UNLOCK_SIGNAL, RECEIVED_MSG_LEN, data_to_file
import RPi.GPIO as GPIO
import gpiozero
import picamera
import vlc
import os
import threading
import socket
import time
import datetime

LOCKED = 2
UNLOCKED = 12
PIN_MOTOR = 11

def server():
	'''
	Server code to receive data from the user
	including a unlock command and
	an audio recording
	'''
	print('Server is running')
	while True:
		conn, _ = server_socket.accept()
		print('Accepted connection from the user')
		while True:
			try:
				message = conn.recv(max(len(UNLOCK_SIGNAL), len(START_AUDIO)))
				if not message:
					conn.close()
					break
				print(message)
				if message == UNLOCK_SIGNAL:
					# Receive the unlock command and turn the motor
					time.sleep(1)
					servo.ChangeDutyCycle(UNLOCKED)

					# unlock for 2 seconds
					time.sleep(2)
					servo.ChangeDutyCycle(LOCKED)

					time.sleep(1)
					conn.send(b'locked')
				elif message == START_AUDIO:
					# Receive the audio recording and play it immediately
					data_to_file(conn, 'in.wav', END_AUDIO, b'received audio')
					vlc.MediaPlayer('in.wav').play()
				else:
					conn.close()
					break
			except:
				conn.close()
				print('Lost connection with the user')
				break

if __name__ == '__main__':
	# Configure GPIO pins on Raspberry Pi
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(PIN_MOTOR, GPIO.OUT)
	servo = GPIO.PWM(PIN_MOTOR, 50)
	camera = picamera.PiCamera()
	btn = gpiozero.Button(4)

	# Get the motor ready to turn
	servo.start(0)
	time.sleep(1)

	# Client socket for sending datetime object, image and audio to the user
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Server socket for listening to the unlock command and receiving audio recording from the user
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect(USER_ADDR_INFO)
		print('Connected to the user')
		server_socket.bind(('', DOORBELL_ADDR_INFO[1]))
		server_socket.listen(1)
		server_thread = threading.Thread(name="server", target=server)
		server_thread.start()
	except:
		client_socket.close()
		server_socket.close()
		print('Failed to connect to the user')
		exit(1)

	while True:
		# Waiting for the doorbell to be pressed
		btn.wait_for_press()
		vlc.MediaPlayer('static/doorbell.mp3').play()

		# Record the current datetime and send it to the user
		client_socket.send(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %w %H:%M:%S').encode())
		print(client_socket.recv(RECEIVED_MSG_LEN)) # b'received date' | b'invalid date'

		# Take a picture and send it to the user
		conn = client_socket.makefile('wb')
		camera.capture(conn, 'jpeg')
		client_socket.send(END_IMAGE)
		print(client_socket.recv(RECEIVED_MSG_LEN)) # b'received image'

		# Record for 3 seconds and send it to the user
		os.system('arecord --duration=3 out.wav')
		with open('out.wav', 'rb') as audio:
			for chunk in audio:
				client_socket.send(chunk)
		client_socket.send(END_AUDIO)
		print(client_socket.recv(RECEIVED_MSG_LEN)) # b'received audio'
