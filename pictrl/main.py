from pi import Pi
from linesocket import LineServer
import os
import re
import time
import threading
import traceback

s = LineServer()
s.initialize()

p = Pi()
p.initialize()

run = True
last_servo = 0.5

def tickPi():
    look_servo = 0.5
    while run:
        time.sleep(1)
        distance = p.get_range()
        print(distance)
        if distance > 5 and distance < 100:
            look_servo = 0.8
            p.set_servo(look_servo)
        elif look_servo is not last_servo:
            look_servo = last_servo
            p.set_servo(last_servo)
        p.tick()

thread = threading.Thread(target=tickPi)
thread.start()

def cheap_sanitize(txt):
    return re.sub(r'[^a-zA-Z0-9_/. ]','',txt)

while run:
    try:
        line = s.next()

        while line is not None:
            print(line)

            words = line.split()

            try:

                if words[0] == "play":
                    os.system("omxplayer "+cheap_sanitize(words[1])+" &")
                    pass

                elif words[0] == "head":
                    val = 0.0
                    val = float(words[1])
                    if val < 0.0:
                        val = 0.0
                    elif val > 100.0:
                        val = 100.0
                    last_servo = val/100.0
                    p.set_servo(last_servo)
                    pass

                elif words[0] == "eye":
                    p.toggle_led()
                    pass

                elif words[0] == "say":
                    words.pop(0)
                    saying = cheap_sanitize(" ".join(words))
                    os.system("echo "+saying+" | festival --tts")
                    pass

                elif words[0] == "range":
                    p.get_range()
                    pass

            except:
                time.sleep(.1)

            line = s.next()
            time.sleep(1)

    except:
        run = False
        s.run = False
        traceback.print_exc()
        time.sleep(1)

p.destruct()

