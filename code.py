import network
import socket
from time import sleep
from machine import Pin, I2C
from pca9685 import PCA9685

SSID = "Airtel_chait"
PASSWORD = "IwontRevealThis"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to WiFi…")
while not wlan.isconnected():
    sleep(0.5)
print("Connected! IP:", wlan.ifconfig()[0])

i2c = I2C(0, scl=Pin(21), sda=Pin(20))
pca = PCA9685(i2c)
pca.freq(50)

servos = {
    "FL": [0, 1],
    "FR": [2, 3],
    "BL": [4, 5],
    "BR": [6, 7],
}

def angle_to_pwm(angle):
    min_us = 500
    max_us = 2500
    us = min_us + (angle/180) * (max_us - min_us)
    duty = int(us / 20000 * 65535)
    return duty

def set_servo(channel, angle):
    duty = angle_to_pwm(angle)
    pca.duty(channel, duty)

def move_leg(leg, yaw_angle, pitch_angle):
    set_servo(servos[leg][0], yaw_angle)
    set_servo(servos[leg][1], pitch_angle)

def stand():
    for leg in servos:
        move_leg(leg, 90, 90)

def forward():
    move_leg("FL", 60, 120)
    move_leg("BR", 60, 120)
    move_leg("FR", 120, 60)
    move_leg("BL", 120, 60)

def backward():
    move_leg("FL", 120, 60)
    move_leg("BR", 120, 60)
    move_leg("FR", 60, 120)
    move_leg("BL", 60, 120)

def left():
    move_leg("FL", 60, 90)
    move_leg("BL", 60, 90)
    move_leg("FR", 120, 90)
    move_leg("BR", 120, 90)

def right():
    move_leg("FL", 120, 90)
    move_leg("BL", 120, 90)
    move_leg("FR", 60, 90)
    move_leg("BR", 60, 90)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Web server running…")

html = """<!DOCTYPE html>
<html>
<head><title>SPOT</title></head>
<body>
<h1>SPOT</h1>
<form>
<button name="cmd" value="forward">F</button>
<button name="cmd" value="backward">B</button>
<button name="cmd" value="left">L</button>
<button name="cmd" value="right">R</button>
<button name="cmd" value="stand">stop</button>
</form>
</body>
</html>
"""

while True:
    cl, addr = s.accept()
    req = cl.recv(1024)
    req = str(req)
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(html)

    if "forward" in req:
        forward()
    elif "backward" in req:
        backward()
    elif "left" in req:
        left()
    elif "right" in req:
        right()
    elif "stand" in req:
        stand()

    cl.close()
