import RPi.GPIO as GPIO
import time

# 핀 설정
BUZZER = 12
SW = [5, 6, 13, 19]   # SW1~SW4

# 음계 주파수 (도레미파솔라시도)
tone = [262, 294, 330, 349, 392, 440, 494, 523]
C, D, E, F, G, A, B, C5 = tone

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER, GPIO.OUT)
for s in SW:
    GPIO.setup(s, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

pwm = GPIO.PWM(BUZZER, 440)
pwm.start(0)

prev = [0, 0, 0, 0]
DEBOUNCE = 0.2
last_time = [0.0, 0.0, 0.0, 0.0]

def play(freq, dur):
    pwm.ChangeFrequency(freq)
    pwm.ChangeDutyCycle(50)
    time.sleep(dur)
    pwm.ChangeDutyCycle(0)
    time.sleep(0.05)

def play_scale():  # 도레미파솔라시도
    for f in tone:
        play(f, 0.3)

def play_effect():  # 나만의 효과음
    seq = [C, E, G, C5, 0, C5, G, E, C]  # 단순 상승+하강
    for f in seq:
        if f == 0:
            pwm.ChangeDutyCycle(0)
        else:
            pwm.ChangeFrequency(f)
            pwm.ChangeDutyCycle(60)
        time.sleep(0.15)
    pwm.ChangeDutyCycle(0)

def play_custom_song():  # 나만의 멜로디 예시
    melody = [C, D, E, G, E, D, C, 0, A, G, E, C]
    for f in melody:
        if f == 0:
            pwm.ChangeDutyCycle(0)
        else:
            pwm.ChangeFrequency(f)
            pwm.ChangeDutyCycle(50)
        time.sleep(0.25)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        curr = [GPIO.input(s) for s in SW]
        now = time.monotonic()

        for i in range(4):
            if prev[i] == 0 and curr[i] == 1 and (now - last_time[i] > DEBOUNCE):
                last_time[i] = now

                if i == 0:
                    print("SW1: 도레미파솔라시도 연주")
                    play_scale()
                elif i == 1:
                    print("SW2: 나만의 효과음")
                    play_effect()
                elif i == 2:
                    print("SW3: 경적 소리")
                    pwm.ChangeFrequency(440)
                    pwm.ChangeDutyCycle(70)
                    time.sleep(0.5)
                    pwm.ChangeDutyCycle(0)
                elif i == 3:
                    print("SW4: 나만의 음악")
                    play_custom_song()

        prev = curr
        time.sleep(0.01)

except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
