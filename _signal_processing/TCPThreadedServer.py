from datetime import datetime
# from json import loads, dumps
import socket
from threading import Thread
from commands import run_command

def example_on_receive_callback(client, address, data, sp):
    cmd, args = data.split(" ", 1)
    cmd = cmd.strip()
    args = args.split(",")
    args = [s.strip() for s in args]

    retArgs, retCount, retData = run_command(cmd, args, sp)
    retArgs = [str(s) for s in retArgs]
    retData = [str(s) for s in retData]
    response = ",".join(retArgs) + "\n" + ",".join(retData) + "\n"

    client.send(response.encode('utf-8'))
    return

def example_on_connected_callback(client, address):
    #print('client connected', client, address)
    # send the client a connection message
#     res = {
#         'cmd': 'connected',
#     }
#     response = dumps(res, default=str)
# #     response = dumps(res, default=str)
#     # add new line chr for TD
#     response += '\n'
#     client.send(response.encode('utf-8'))
    return

def example_on_disconnected_callback(client, address):
    #print('client disconnected', client, address)
    return


#class TCPThreadedServer:
class TCPThreadedServer(Thread):
    def __init__(
            self,
            host,
            port,
            sp,
            timeout=60,
            on_connected_callback=example_on_connected_callback,
            on_receive_callback=example_on_receive_callback,
            on_disconnected_callback=example_on_disconnected_callback,
            debug=False,
            debug_data=False
            ):

        self.host = host
        self.port = port
        self.timeout = timeout
        self.decode_json = False
        self.on_connected_callback = on_connected_callback
        self.on_receive_callback = on_receive_callback
        self.on_disconnected_callback = on_disconnected_callback
        self.debug = debug
        self.debug_data = debug_data
        self.clients = []
        self.sp = sp
        Thread.__init__(self)

#    def start(self):
#        self.run()

    # run by the Thread object
    def run(self):
        if self.debug:
            print(datetime.now(), 'SERVER Starting...', '\n')

        self.listen()

    def listen(self):
        # create an instance of socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to its host and port
        self.sock.bind((self.host, self.port))
        if self.debug:
            print(datetime.now(), 'SERVER Socket Bound', self.host, self.port, '\n')

        # start listening for a client
        self.sock.listen(5)
        if self.debug:
            print(datetime.now(), 'SERVER Listening...', '\n')
        
        while True:
            # get the client object and address
            client, address = self.sock.accept()

            # add client to list
            self.clients.append(client)

            # set a timeout
            client.settimeout(self.timeout)

            if self.debug:
                print(datetime.now(), 'CLIENT Connected', client, '\n')

            if self.on_connected_callback:
                self.on_connected_callback(client, address)

            # start a thread to listen to the client
            Thread(
                target=self.listen_to_client,
                args=(client, address, self.decode_json, self.on_receive_callback, self.on_disconnected_callback)
            ).start()

    def listen_to_client(self, client, address, decode_json, on_receive_callback, on_disconnected_callback):
        # set a buffer size ( could be 2048 or 4096 / power of 2 )
        size = 1024*1024
        while True:
            try:
                d = client.recv(size)
                if d:
                    #messages = d.split(b'\n\r')
                    messages = d.split(b'\0')

                    for data in messages:
                        if data:
                            data = data.decode('utf-8')

                            if self.debug:
                                print(datetime.now(), 'CLIENT Data Received', address)
                                if not self.debug_data:
                                    print('\n')

#                             if decode_json:
#                                 try:
#                                     data = loads(data)
#                                 except Exception as e:
#                                     if self.debug:
#                                         print(datetime.now(), 'CLIENT Json Failed:', data, '\n', e, '\n')
#                                     break

                            if self.debug_data:
                                print(data, '\n')

                            if on_receive_callback:
                                try:
                                    on_receive_callback(client, address, data, self.sp)
                                except Exception as e:
                                    if self.debug:
                                        print(datetime.now(), 'CLIENT Receive Callback Failed:', data, '\n', e, '\n')
                else:
                    raise ValueError('CLIENT Disconnected')

            except Exception as e:
                if self.debug:
                    print(datetime.now(), e, client, '\n')

                client.close()
                client_index = self.clients.index(client)

                self.clients.pop(client_index)

                if on_disconnected_callback:
                    try:
                        on_disconnected_callback(client, address)
                    except Exception as e:
                        print('on_close_callback failed\n', e, '\n')
                return False

if __name__ == "__main__":
    TCPThreadedServer(
        '127.0.0.1',
        8008,
        timeout=86400,
        decode_json=False,
        debug=True,
        debug_data=True
    ).start()
