from gpiozero import Button
import socket
import time
import os

btn = Button(4)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST='192.168.137.46'
PORT=8888

try:
	client_socket.connect((HOST,PORT))
	print('connected')
except:
	print('connect failed')

while True:
	btn.wait_for_press()
	os.system('arecord --format=S16_LE --rate=16000 --file-type=wav --duration=1 out.wav')
	with open('out.wav', 'rb') as recording:
		for chunk in recording:
			client_socket.send(chunk)
	print(client_socket.recv(1000))
