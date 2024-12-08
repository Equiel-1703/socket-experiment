import socket
import re
import datetime
from threading import Thread
from random import randint

def createServerSocket(server_ip, server_port, kind = 'UDP') -> socket.socket:
	kind = kind.upper()
	server_kind: socket.SocketKind = None
	
	if kind == 'UDP':
		server_kind = socket.SOCK_DGRAM
	else:
		server_kind = socket.SOCK_STREAM # Use TCP if not 'UDP'

	server_socket = socket.socket(socket.AF_INET, server_kind)
	server_socket.bind((server_ip, server_port))

	return server_socket

def createClientSocket(kind = 'UDP', timeout = -1) -> socket.socket:
	kind = kind.upper()
	client_kind: socket.SocketKind = None
	
	if kind == 'UDP':
		client_kind = socket.SOCK_DGRAM
	else:
		client_kind = socket.SOCK_STREAM # Use TCP if not 'UDP'

	client_socket = socket.socket(socket.AF_INET, client_kind)
	
	if timeout > 0:
		client_socket.settimeout(timeout)

	return client_socket

def serverThread(args):
	server_ip = args[0]
	server_port = args[1]

	print_buffer.append(f'ServerThread> Creating server in {server_ip}:{server_port}')
	try:
		server_socket = createServerSocket(server_ip, server_port)
		print_buffer.append('ServerThread> Server socket created successfully.')
	except Exception as e:
		print_buffer.append(f'ServerThread> Error creating server socket: {e}')
		return
	
	try:
		while True:
			data, client_address = server_socket.recvfrom(1024)
			decoded_data = data.decode().strip().upper()

			print_buffer.append(f'ServerThread> Message received from client: {decoded_data}')

			if decoded_data == 'EXIT':
				print_buffer.append('ServerThread> Closing server...')
				server_socket.sendto('Bye, client!.'.encode(), client_address)
				break
			else:
				if re.match(r'^HELLO|^HI', decoded_data):
					response = "Hello, client!"
				elif re.match(r'^DO THE MJ', decoded_data):
					response = "Hee-hee!"
				elif re.match(r'^WHAT ARE YOU LISTENING TO', decoded_data):
					response = ["I'm listening to Billie Jean by Michael Jackson.", "Some bytes B)"][randint(0, 1)]
				elif re.match(r'^WHAT.*TIME', decoded_data):
					response = f"It's {datetime.datetime.now().time().strftime('%H:%M:%S')}."
				elif re.match(r'^WHAT.*DATE', decoded_data):
					response = f"It's {datetime.datetime.now().date().strftime('%d/%m/%Y')}."
				elif re.match(r'^WHAT IS YOUR NAME', decoded_data):
					response = "I'm Server 8000. Nice to meet you!"
				elif re.match(r'^WHAT IS YOUR FAVORITE COLOR', decoded_data):
					response = "I'm colorblind, but I like blue!"
				else:
					response = "Message received successfully."

				print_buffer.append(f'ServerThread> Sending response to client...')
				server_socket.sendto(response.encode(), client_address)
		
		server_socket.close()
	except Exception as e:
		print_buffer.append(f'ServerThread> Error: {e}')

	print_buffer.append('ServerThread> Server closed.')

terminate_print_thread = False
print_buffer = []

def printThread():
	while (not terminate_print_thread) or len(print_buffer) > 0:
		if len(print_buffer) > 0:
			print(print_buffer.pop(0))

if __name__ == '__main__':
	server_ip = 'localhost'
	server_port = 8_000

	# Starting print thread
	print_thread = Thread(target=printThread)
	print_thread.start()

	# Starting server thread
	server_thread = Thread(target=serverThread, args=((server_ip, server_port),))
	server_thread.start()

	# Creating client socket
	client_socket = createClientSocket(timeout = 5)

	while True:
		print_buffer.append('Client> Enter message to send to server:')
		message = input().strip()

		try:
			client_socket.sendto(message.encode()[:1024], (server_ip, server_port))
			response = client_socket.recvfrom(1024)
			decoded_response = response[0].decode()
			print_buffer.append(f'Client> Message from server: {decoded_response}')
		except socket.timeout:
			print_buffer.append(f'Client> Server did not respond within {client_socket.gettimeout()} seconds.')
		finally:
			if message == 'exit':
				break
	
	server_thread.join() # Wait for server thread to finish

	terminate_print_thread = True
	print_thread.join() # Wait for print thread to finish

	client_socket.close()
	print('Client> Client closed.')
