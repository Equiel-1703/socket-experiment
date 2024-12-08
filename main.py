import socket
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

def serverFunction(args):
	server_ip = args[0]
	server_port = args[1]

	print(f'ServerThread> Creating server in {server_ip}:{server_port}...')
	try:
		server_socket = createServerSocket(server_ip, server_port)
		print('ServerThread> Server socket created successfully.')
	except Exception as e:
		print(f'ServerThread> Error creating server socket: {e}')
	
	try:
		while True:
			data, client_address = server_socket.recvfrom(1024)
			decoded_data = data.decode().strip().upper()

			print(f'ServerThread> Received data from {client_address}: {decoded_data}')

			if decoded_data == 'EXIT':
				print('ServerThread> Exiting server...')
				server_socket.sendto('Server closed.'.encode(), client_address)
				break
			else:
				if decoded_data == 'HELLO':
					response = "Hello, client!"
				elif decoded_data == 'DO THE MJ':
					response = "Hee-hee!"
				elif decoded_data == 'WHAT ARE YOU LISTENING TO?':
					response = ["I'm listening to Billie Jean by Michael Jackson.", "Some bytes B)"][randint(0, 1)]
				else:
					response = "Message received successfully."

				print('ServerThread> Sending response to client...')
				server_socket.sendto(response.encode(), client_address)
		
		server_socket.close()
	except Exception as e:
		print(f'ServerThread> Error receiving data: {e}')

	print('ServerThread> Server closed.')

if __name__ == '__main__':
	server_ip = 'localhost'
	server_port = 8000

	server_thread = Thread(target=serverFunction, args=((server_ip, server_port),))
	server_thread.start()

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	client_socket.settimeout(5) # Will wait 5 seconds for a response

	while True:
		message = input('Type a message to send to the server: ')

		try:
			client_socket.sendto(message.encode(), (server_ip, server_port))
			response = client_socket.recvfrom(1024)
			decoded_response = response[0].decode()
			print(f'Client> Server response: {decoded_response}')
		except socket.timeout:
			print('Client> Server did not respond within 5 seconds.')
		finally:
			if message == 'exit':
				break
	
	server_thread.join() # Wait for server thread to finish
	client_socket.close()
	print('Client> Client closed.')
