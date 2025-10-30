import RPi.GPIO as GPIO
import time

PINS = [5, 6, 13, 19]                # SW1~SW4 (BCM)
N = len(PINS)
DEBOUNCE_SEC = 0.2                    # 소프트 디바운스

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for p in PINS:
    GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

prev_states = [0] * N                 # 직전 GPIO 값
counts      = [0] * N                 # 클릭 횟수
last_time   = [0.0] * N               # 마지막 클릭 시각 (디바운스용)
names       = [f"SW{i+1}" for i in range(N)]

try:
    while True:
        # 현재 GPIO 값 일괄 읽기
        curr_states = [GPIO.input(p) for p in PINS]
        now = time.monotonic()

        for i, (prev, curr) in enumerate(zip(prev_states, curr_states)):
            # 0 -> 1 상승엣지에서만 동작
            if prev == 0 and curr == 1:
                # 디바운스 (연속 바운스 방지)
                if now - last_time[i] >= DEBOUNCE_SEC:
                    counts[i] += 1
                    print((f"{names[i]} click", counts[i]))
                    last_time[i] = now

        # 이번 값을 다음 반복의 이전값으로 저장
        prev_states = curr_states
        time.sleep(0.01)              # 폴링 주기 (10ms)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
