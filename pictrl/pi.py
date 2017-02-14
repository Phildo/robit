import RPi.GPIO as GPIO
import time

LED_PIN = 11
SERVO_PIN = 18
PWM_HERZ = 50
#SERVO_CW = 0.6*1000
#SERVO_CCW = 2.1*1000
SERVO_CW = 3.5
SERVO_CCW = 11.0
RANGE_PIN = 13

class Pi():

    def __init__(self):
        pass

    def initialize(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.setup(SERVO_PIN, GPIO.OUT)

        self.led_state = False
        self.set_led(False)

        self.pwm_time_on = time.time()-100
        self.pwm_ctrl = GPIO.PWM(SERVO_PIN,PWM_HERZ)
        self.pwm_on = False

        self.locked = False

    def perctoservo(self,perc):
        return SERVO_CW+(perc*(SERVO_CCW-SERVO_CW))

    def set_led(self,state):
        if(state):
            self.led_state = True
            GPIO.output(LED_PIN,GPIO.HIGH)
        else:
            self.led_state = False
            GPIO.output(LED_PIN,GPIO.LOW)

    def toggle_led(self):
        self.set_led(not self.led_state)

    def set_servo(self,percent):
        while self.locked:
            print("Locked, waiting...")
            time.sleep(1)

        if not self.pwm_on:
            print("PWM start")
            self.pwm_ctrl = GPIO.PWM(SERVO_PIN,PWM_HERZ)
            self.pwm_ctrl.start(self.perctoservo(percent))
        else:
            self.pwm_ctrl.ChangeDutyCycle(self.perctoservo(percent))
        self.pwm_time_on = time.time()
        self.pwm_on = True

    def get_range(self):
        invmicro = 1000000
        GPIO.setup( RANGE_PIN,GPIO.OUT)
        GPIO.output(RANGE_PIN,GPIO.LOW)
        ticks = 0
        cur = time.perf_counter()
        while time.perf_counter() - cur < 2/invmicro:
          ticks += 1
        time.sleep(2/invmicro)
        GPIO.output(RANGE_PIN,GPIO.HIGH)
        cur = time.perf_counter()
        while time.perf_counter()-cur < 5/invmicro:
          ticks += 1
        time.sleep(2/invmicro)
        time.sleep(5/invmicro)
        GPIO.output(RANGE_PIN,GPIO.LOW)
        GPIO.setup( RANGE_PIN,GPIO.IN)

        distance = 0
        timedout = False

        timeout = 0.001
        starttime = time.perf_counter()
        while GPIO.input(RANGE_PIN) == 0 and not timedout:
            if(time.perf_counter() - starttime > timeout):
                timedout = True

        if not timedout:
            timeout = 0.05
            starttime = time.perf_counter()
            while GPIO.input(RANGE_PIN) == 1 and not timedout:
                if(time.perf_counter() - starttime > timeout):
                    timedout = True

        if not timedout:
            distance = (time.perf_counter() - starttime)*invmicro/29/2
        else:
            print("timed out :(")

        return distance

    def tick(self):
        self.locked = True
        if self.pwm_on and time.time()-self.pwm_time_on > 3:
            print("PWM stop")
            self.pwm_ctrl.stop()
            self.pwm_on = False
        self.locked = False

    def destruct(self):
        self.pwm_ctrl.stop()
        GPIO.cleanup()

