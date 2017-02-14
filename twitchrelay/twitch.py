import string
import socket
import time
from collections import deque
from config import HOST,PORT,PASS,IDENT,CHANNEL

class Twitch():

    def __init__(self):
        pass

    def sendMessage(self, message):
        messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
        self.s.send(bytes(messageTemp + "\r\n", 'UTF-8'))

    def getUser(self, line):
        separate = line.split(":", 2)
        user = separate[1].split("!", 1)[0]
        return user

    def getMessage(self, line):
        separate = line.split(":", 2)
        message = separate[2]
        return message

    def initialize(self):

        # opens socket
        self.s = socket.socket()
        self.s.connect((HOST, PORT))
        self.s.send(bytes("PASS " + PASS + "\r\n", 'UTF-8'))
        self.s.send(bytes("NICK " + IDENT + "\r\n", 'UTF-8'))
        self.s.send(bytes("JOIN #" + CHANNEL + "\r\n", 'UTF-8'))

        # joins room
        self.readbuffer = ""
        Loading = True
        while Loading:
            received = self.s.recv(1024)
            self.readbuffer = self.readbuffer + received.decode('utf-8')
            temp = str.split(self.readbuffer, "\n")
            self.readbuffer = temp.pop()

            for line in temp:
                Loading = not ("End of /NAMES list" in line)

        # initialize properties
        self.readbuffer = ""
        self.q = deque([])

    def tick(self):
        received = self.s.recv(1024)
        self.readbuffer = self.readbuffer + received.decode('utf-8')
        if(len(received) == 0):
            time.sleep(.1)
            self.s.close()
            self.initialize()

        temp = str.split(self.readbuffer, "\n")
        self.readbuffer = temp.pop()

        for line in temp:
            if "PING" in line:
                self.s.send(bytes(line.replace("PING", "PONG")+"\n", 'UTF-8'))
            else:
                self.q.appendleft(self.getMessage(line))

    def next(self):
        if len(self.q) > 0:
            return self.q.pop()
        else:
            return None

