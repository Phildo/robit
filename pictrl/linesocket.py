import threading
import string
import socket
import select
import time
import queue
from collections import deque

quick_timeout = 1

class LineClient():

    def __init__(self):
        self.s = None
        self.readbuffer = ""
        self.q = deque([])
        self.host = "127.0.0.1"
        self.port = 50817
        self.fail_count = 0
        pass

    def initialize(self, port = None, host = None):
        if port is not None:
            self.port = port
        if host is not None:
            self.host = host
        self.s = socket.socket()
        self.s.connect((self.host, self.port))
        self.readbuffer = ""
        self.q = deque([])

    def tick(self):
        received = self.s.recv(1024)
        self.readbuffer = self.readbuffer + received.decode('utf-8')
        if(len(received) == 0):
            self.fail_count += 1
        else:
            self.fail_count = 0

            lines = str.split(self.readbuffer, "\n")
            self.readbuffer = lines.pop()

            for line in lines:
                self.q.appendleft(line)

    def retry(self):
        self.s.close()
        time.sleep(.1*pow(2,self.fail_count))
        self.initialize()

    def next(self):
        if len(self.q) > 0:
            return self.q.pop()
        else:
            return None

    def send(self,text):
        try:
            self.s.send(bytes(text + "\n",'UTF-8'))
        except:
            self.fail_count += 1
            raise

    def destruct(self):
        if self.s is not None:
            self.s.close()

class LineServer():

    def __init__(self):
        self.s = None
        self.local = True
        self.port = 50817
        self.fail_count = 0
        self.run = True

        self.new_client_socks = queue.Queue();
        self.clients = []
        self.q = queue.Queue()
        pass

    def initialize(self, port = None, local = None):
        if port is not None:
            self.port = port
        if local is not None:
            self.local = local
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.local:
            self.s.bind(("127.0.0.1", self.port))
        else:
            self.s.bind((socket.gethostname(), self.port))

        self.s.settimeout(quick_timeout)
        self.s.listen(5)

        server_thread = threading.Thread(target = self.threadserver)
        server_thread.start()
        client_thread = threading.Thread(target = self.threadclients)
        client_thread.start()

    def tickserver(self):
        #print("server tickserver")
        try:
            clientsocket, address = self.s.accept()
            self.new_client_socks.put(clientsocket)
            print("server accepted client socket")
        except socket.timeout:
            pass

    def threadserver(self):
        while self.run:
            self.tickserver()

    def tickclients(self):
        #print("server tickclient")
        while not self.new_client_socks.empty():
            s = self.new_client_socks.get()
            s.setblocking(0)
            client = LineClient()
            client.s = s
            self.clients.append(client)

        listen_for_read   = []
        for client in self.clients:
            listen_for_read.append(client.s)
        listen_for_write  = []
        listen_for_except = []
        for client in self.clients:
            listen_for_except.append(client.s)
        try:
            readables, writables, exceptionals = select.select(listen_for_read,listen_for_write,listen_for_except,quick_timeout)
        except socket.timeout:
            pass

        for readable in readables:
            for client in self.clients:
                if readable == client.s:
                    client.tick()

        #check for client's failure or exception
        clients_len = len(self.clients)
        for i in range(clients_len):
            index = clients_len-i-1
            client = self.clients[index]
            if client.fail_count:
                print("server killing failed client")
                client.destruct()
                self.clients.pop(index)
            else:
                for exceptional in exceptionals:
                    if exceptional == client.s:
                        print("server killing exceptional client")
                        client.destruct()
                        self.clients.pop(index)

        for client in self.clients:
            line = client.next()
            while line is not None:
                #print("server found line:" + line)
                self.q.put(line)
                line = client.next()

    def threadclients(self):
        while self.run:
            self.tickclients()

    def next(self):
        if self.q.qsize() > 0:
            return self.q.get()
        else:
            return None

