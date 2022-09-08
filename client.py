from gpiozero import Button
import RPi.GPIO as GPIO
import socket
import time
import os

GPIO.setmode(GPIO.BOARD)
btn = Button(4)

PIN_MOTOR = 11
GPIO.setup(PIN_MOTOR, GPIO.OUT)
servo = GPIO.PWM(PIN_MOTOR, 50)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST='172.20.10.2'
PORT=8888
locked = 2
unlocked = 12

try:
	client_socket.connect((HOST,PORT))
	print('connected')
except:
	print('connect failed')

servo.start(0)
time.sleep(1)
while True:
	btn.wait_for_press()

	servo.ChangeDutyCycle(locked)
	time.sleep(1)

	servo.ChangeDutyCycle(unlocked)
	time.sleep(1)

	servo.ChangeDutyCycle(locked)
	time.sleep(1)

	#os.system('arecord --format=S16_LE --rate=16000 --file-type=wav --duration=1 out.wav')
	#with open('out.wav', 'rb') as recording:
	#	for chunk in recording:
	#		client_socket.send(chunk)
	#print(client_socket.recv(1000))
