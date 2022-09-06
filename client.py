from gpiozero import Button
import socket
import time
btn = Button(4)
mySocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST='192.168.137.46'
PORT=8888
try:
	mySocket.connect((HOST,PORT))
	print("connected")
except:
	print('connect failed')
while True:
	btn.wait_for_press()
	with open('.ssh/id_rsa.pub', 'r') as ssh:
		key = ssh.read()
		print(key)
		mySocket.send(key.encode())
	time.sleep(1)
