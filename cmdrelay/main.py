from linesocket import LineClient
import time
import traceback

c = LineClient()
c.initialize()

run = True

while run:
    try:
        message = input("MSG: ")
        c.send(message)
    except:
        run = False
        traceback.print_exc()
        time.sleep(.1)

