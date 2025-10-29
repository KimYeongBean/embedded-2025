import RPi.GPIO as GPIO
import time

SW1 = 5
SW2 = 6
SW3 = 13
SW4 = 19

PWMA = 18
PWMB = 23
AIN1 = 22
AIN2 = 27
BIN1 = 25
BIN2 = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(PWMA,GPIO.OUT)
GPIO.setup(PWMB,GPIO.OUT)

GPIO.setup(AIN1,GPIO.OUT)
GPIO.setup(AIN2,GPIO.OUT)
GPIO.setup(BIN1,GPIO.OUT)
GPIO.setup(BIN2,GPIO.OUT)

GPIO.setup(SW1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW2,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW3,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW4,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

L_Motor = GPIO.PWM(PWMA,500)
L_Motor.start(0)
R_Motor = GPIO.PWM(PWMB,500)
R_Motor.start(0)

try:
    while True:
        sw1Value = GPIO.input(SW1)
        sw2Value = GPIO.input(SW2)
        sw3Value = GPIO.input(SW3)
        sw4Value = GPIO.input(SW4)

        if sw1Value == 1: # front
            print('SW1 click')
            GPIO.output(AIN1,0)
            GPIO.output(AIN2,1)
            GPIO.output(BIN1,0)
            GPIO.output(BIN2,1)

            L_Motor.ChangeDutyCycle(50)
            R_Motor.ChangeDutyCycle(50)
        elif sw2Value == 1: # right
            print('SW2 click')
            GPIO.output(AIN1,0)
            GPIO.output(AIN2,1)
            GPIO.output(BIN1,1)
            GPIO.output(BIN2,0)

            L_Motor.ChangeDutyCycle(50)
            R_Motor.ChangeDutyCycle(50)
        elif sw3Value == 1: # left
            print('SW3 click')
            GPIO.output(AIN1,1)
            GPIO.output(AIN2,0)
            GPIO.output(BIN1,0)
            GPIO.output(BIN2,1)

            L_Motor.ChangeDutyCycle(50)
            R_Motor.ChangeDutyCycle(50)
        elif sw4Value == 1: # back
            print('SW4 click')
            GPIO.output(AIN1,1)
            GPIO.output(AIN2,0)
            GPIO.output(BIN1,1)
            GPIO.output(BIN2,0)

            L_Motor.ChangeDutyCycle(50)
            R_Motor.ChangeDutyCycle(50)

        else:
            L_Motor.ChangeDutyCycle(0)
            R_Motor.ChangeDutyCycle(0)
        
        time.sleep(1.0)

except KeyboardInterrupt:
    pass

GPIO.cleanup()