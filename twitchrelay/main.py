from linesocket import LineClient
from twitch import Twitch
import re
import time
import traceback

t = Twitch()
t.initialize()
t.sendMessage("robit reporting for duty")

c = LineClient()
c.initialize()

song_t = 0
run = True

def cheap_sanitize(txt):
    return re.sub(r'[^a-zA-Z0-9_/. ]','',txt)

def reallysend(txt):
    sent = False
    while run and not sent:
        try:
            c.send(txt)
            sent = True
        except:
            c.retry()

while run:
    try:
        t.tick()
        line = t.next()

        while line is not None:
            print("received: "+line)
            words = line.split(" ");

            if time.time()-song_t > 60*5 and "black" in line:
                reallysend("play ../mouth/black.mp3")
                song_t = time.time()
            if time.time()-song_t > 60*5 and "300" in line:
                reallysend("play ../mouth/300.mp3")
                song_t = time.time()
            if time.time()-song_t > 60*5 and "dinosaur" in line:
                reallysend("play ../mouth/dinosaur.mp3")
                song_t = time.time()
            if time.time()-song_t > 60*5 and "bustin" in line:
                reallysend("play ../mouth/bustin.mp3")
                song_t = time.time()
            if time.time()-song_t > 60*5 and "tiger" in line:
                reallysend("play ../mouth/tiger.mp3")
                song_t = time.time()
            if time.time()-song_t > 60*5 and "youngman" in line:
                reallysend("play ../mouth/youngman.mp3")
                song_t = time.time()
            if time.time()-song_t > 60*5 and "harrison" in line:
                reallysend("play ../mouth/harrison.mp3")
                song_t = time.time()
            if time.time()-song_t > 60*5 and "week" in line:
                reallysend("play ../mouth/week.mp3")
                song_t = time.time()

            if words[0] == "robit":
                words.pop(0)
                line = " ".join(words)
                reallysend(cheap_sanitize(line))

            line = t.next()
            time.sleep(1)

        time.sleep(1)

    except:
        run = False
        traceback.print_exc()
        time.sleep(1)

