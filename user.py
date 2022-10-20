from helper import USER_ADDR_INFO, END_AUDIO, END_IMAGE, RECEIVED_AUDIO, RECEIVED_IMAGE, DATE_LEN, data_to_file
from routes import APP, update
import os
import socket
import datetime
import threading
import signal
import yaml
import plot

DATETIMES: list[datetime.datetime] = []

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
				data_to_file(conn, 'static/assets/in.jpeg', END_IMAGE, RECEIVED_IMAGE)
				data_to_file(conn, 'static/assets/in.wav', END_AUDIO, RECEIVED_AUDIO)

				# Set the flag so the frontend can receive an update
				update()
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
		server_socket.close()
		exit(0)

	signal.signal(signal.SIGINT, handler)
