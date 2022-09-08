from gpiozero import Button
import RPi.GPIO as GPIO
import socket
import time
import threading
import os

LOCKED = 2
UNLOCKED = 12

PIN_MOTOR = 11

def server():
	print('server is running')
	while True:
		try:
			conn, _ = server_socket.accept()
			print('accepted connection from user')
			while True:
				message = conn.recv(6)
				print(message)
				if message == b'unlock':
					servo.ChangeDutyCycle(LOCKED)
					time.sleep(1)

					servo.ChangeDutyCycle(UNLOCKED)
					time.sleep(1)

					servo.ChangeDutyCycle(LOCKED)
					time.sleep(1)

					conn.send(b'unlocked')
		except:
			conn.close()

if __name__ == '__main__':
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(PIN_MOTOR, GPIO.OUT)
	servo = GPIO.PWM(PIN_MOTOR, 50)
	btn = Button(4)

	servo.start(0)
	time.sleep(1)
	print('Motor is ready to go')

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		client_socket.connect(('172.20.10.2', 9000))
		print('connected to user')

		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind(('', 8000))
		server_socket.listen(1)
		server_thread = threading.Thread(name="server", target=server)
		server_thread.start()
	except:
		client_socket.close()
		server_socket.close()
		print('something went wrong')
		exit()

	while True:
		btn.wait_for_press()

		os.system('arecord --format=S16_LE --rate=16000 --file-type=wav --duration=1 out.wav')
		with open('out.wav', 'rb') as recording:
			for chunk in recording:
				client_socket.send(chunk)
		os.system('aplay out.wav')
