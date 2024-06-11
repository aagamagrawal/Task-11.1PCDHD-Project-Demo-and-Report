from bluepy.btle import Peripheral, UUID
import RPi.GPIO as GPIO
import time
import smtplib
import serial

# Define GPIO pins
GREEN_LED_PIN = 17
RED_LED_PIN = 27
BUZZER_PIN = 22

# Define threshold values
FLAME_THRESHOLD = 90
TEMP_THRESHOLD = 38
MQ2_THRESHOLD = 35
CO_THRESHOLD = 55

# GSM module setup
gsm_serial = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)

# Email setup
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL = 'your_email@gmail.com'
PASSWORD = 'your_email_password'
TO_EMAIL = 'alert_recipient@gmail.com'

def send_sms_alert():
    gsm_serial.write(b'ATD+61478890148;\r')

def send_email_alert():
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    subject = 'Fire Alert!'
    body = 'Fire has been detected. Immediate action required!'
    msg = f'Subject: {subject}\n\n{body}'
    server.sendmail(EMAIL, TO_EMAIL, msg)
    server.quit()

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def process_sensor_data(flame, temp, mq2, co):
    if flame > FLAME_THRESHOLD and temp > TEMP_THRESHOLD and mq2 > MQ2_THRESHOLD and co > CO_THRESHOLD:
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        send_sms_alert()
        send_email_alert()
    else:
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)

def main():
    setup_gpio()
    
    # Replace 'xx:xx:xx:xx:xx:xx' with the MAC address of your Arduino Nano 33 IoT
    p = Peripheral('xx:xx:xx:xx:xx:xx')

    flame_uuid = UUID('2A56')
    temp_uuid = UUID('2A6E')
    mq2_uuid = UUID('2A77')
    co_uuid = UUID('2A79')

    while True:
        try:
            flame = p.readCharacteristic(flame_uuid)
            temp = p.readCharacteristic(temp_uuid)
            mq2 = p.readCharacteristic(mq2_uuid)
            co = p.readCharacteristic(co_uuid)
            
            flame_value = int.from_bytes(flame, byteorder='little')
            temp_value = float(temp.decode('utf-8'))
            mq2_value = int.from_bytes(mq2, byteorder='little')
            co_value = int.from_bytes(co, byteorder='little')

            process_sensor_data(flame_value, temp_value, mq2_value, co_value)
            
            time.sleep(2)
        except Exception as e:
            print(f'Error: {e}')
            p.disconnect()
            break

if __name__ == "__main__":
    main()
