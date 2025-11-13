import RPi.GPIO as GPIO
import time
import serial
import threading

PWMA = 18
AIN1 = 22
AIN2 = 27
PWMB = 23
BIN1 = 25
BIN2 = 24

SPEED = 100
TURN_SPEED = 50

SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 9600

gData = ""
gData_lock = threading.Lock()

running = True

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

L_Motor = GPIO.PWM(PWMA, 500)
R_Motor = GPIO.PWM(PWMB, 500)
L_Motor.start(0)
R_Motor.start(0)


# 모터 제어 함수
def set_motor_speeds(left_speed, right_speed):
    L_Motor.ChangeDutyCycle(abs(left_speed))
    R_Motor.ChangeDutyCycle(abs(right_speed))

def set_motor_direction(left_forward, right_forward):
    GPIO.output(AIN1, not left_forward)
    GPIO.output(AIN2, left_forward)
    GPIO.output(BIN1, not right_forward)
    GPIO.output(BIN2, right_forward)

def go_forward():
    set_motor_direction(True, True)
    set_motor_speeds(SPEED, SPEED)

def go_backward():
    set_motor_direction(False, False)
    set_motor_speeds(SPEED, SPEED)

def turn_left():
    set_motor_direction(False, True)
    set_motor_speeds(SPEED, SPEED)

def turn_right():
    set_motor_direction(True, False)
    set_motor_speeds(SPEED, SPEED)

def go_forward_left():
    set_motor_direction(True, True)
    set_motor_speeds(TURN_SPEED, SPEED)

def go_forward_right():
    set_motor_direction(True, True)
    set_motor_speeds(SPEED, TURN_SPEED)

def go_backward_left():
    set_motor_direction(False, False)
    set_motor_speeds(TURN_SPEED, SPEED)

def go_backward_right():
    set_motor_direction(False, False)
    set_motor_speeds(SPEED, TURN_SPEED)

def stop():
    set_motor_speeds(0, 0)

# 조이스틱 신호 함수
def parse_joystick_signal(signal_str):
    try:
        signal_str = signal_str.strip()
        data = signal_str.replace("J0:", "")
        parts = data.split(",")
        angle = float(parts[0])
        magnitude = float(parts[1])
        return angle, magnitude
    except (ValueError, IndexError):
        return None, None

# 조이스틱 각도에 따른 동작 결정
def joystick_to_movement(angle, magnitude, threshold=0.1):
    move_action = "Stop"
    
    if magnitude < threshold:
        stop()
        return "Stop"
    
    angle = angle % 360
    
    if 22.5 <= angle < 67.5:
        go_forward_right()
        move_action = "Forward-Right"
    elif 67.5 <= angle < 112.5:
        go_forward()
        move_action = "Forward"
    elif 112.5 <= angle < 157.5:
        go_forward_left()
        move_action = "Forward-Left"
    elif 157.5 <= angle < 202.5:
        turn_left()
        move_action = "Left Turn"
    elif 202.5 <= angle < 247.5:
        go_backward_left()
        move_action = "Backward-Left"
    elif 247.5 <= angle < 292.5:
        go_backward()
        move_action = "Backward"
    elif 292.5 <= angle < 337.5:
        go_backward_right()
        move_action = "Backward-Right"
    elif 337.5 <= angle or angle < 22.5:
        turn_right()
        move_action = "Right Turn"
    
    return move_action

# 시리얼 수신 Thread
def serial_thread():
    global gData, running
    
    try:
        bleSerial = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=1.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        print(f"시리얼 포트 열음: {SERIAL_PORT}")
        
        while running:
            try:
                if bleSerial.in_waiting > 0:
                    raw_data = bleSerial.readline()

                    try:
                        data = raw_data.decode('utf-8')
                    except (UnicodeDecodeError, AttributeError):
                        # 디코딩 오류 발생 시 기본값으로 처리
                        data = "J0:0,0.0\n"
                        print(f"시리얼 수신 오류 - 기본값으로 처리")
                    
                    if data:
                        with gData_lock:
                            gData = data
                        print(f"수신: {data.strip()}")
            except Exception as e:
                print(f"시리얼 수신 오류: {e}")
                time.sleep(0.1)
        
        bleSerial.close()
    
    except serial.SerialException as e:
        print(f"시리얼 포트 오류: {e}")

# 메인 실행 함수
def main():
    global gData, running, buzzer_start_time
    
    move_action = "Stop"
    horn_status = "Off"
    
    try:
        while running:
            current_time = time.time()
            
            with gData_lock:
                data = gData
                gData = ""
            
            if data:
                # 조이스틱 신호 처리
                if data.startswith("J0:"):
                    angle, magnitude = parse_joystick_signal(data)
                    if angle is not None:
                        move_action = joystick_to_movement(angle, magnitude)
            
            # 화면 출력
            print(f"\rMovement: {move_action:<15} | Horn: {horn_status}", end="", flush=True)
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n프로그램 종료 중...")
        running = False
        time.sleep(0.5)
    
    finally:
        stop()
        sound_off()
        GPIO.cleanup()
        print("GPIO cleaned up and program terminated.")

if __name__ == '__main__':
    task1 = threading.Thread(target=serial_thread, daemon=True)
    task1.start()

    main()