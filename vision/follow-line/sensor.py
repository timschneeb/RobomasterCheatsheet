from queue import Queue
import math
from robomaster import robot

queue = Queue()

robot = robot.Robot()

# RGB Farbverlauf Rot-Gelb-Grün für LEDs berechnen
def percent_to_rgb(percent):
    if percent == 100:
        percent = 99

    # Quelle: https://stackoverflow.com/questions/340209/generate-colors-between-red-and-green-for-a-power-meter
    if percent < 50:
        r = math.floor(255 * (percent / 50.0))
        g = 255
    else:
        r = 255
        g = math.floor(255 * ((50 - percent % 50.0) / 50.0))

    return [r, g, 0]

def translate(value, leftMin, leftMax, rightMin, rightMax):
    return rightMin + (float(value - leftMin) / float(leftMax - leftMin) * rightMax - rightMin)

def cb_distance(val):
    global robot
    left = val[0]

    queue.put(left)

# robot.initialize(conn_type="sta", sn="3JKDH63001E06B")
robot.initialize(conn_type="ap")

distanceSensor = robot.sensor
# cb_distance 5mal pro Sekunde mit Entfernungsdaten versorgen
distanceSensor.sub_distance(10, cb_distance)

while True:
    distance = queue.get()

    if not queue.empty:
        queue.clear()

    percent = translate(distance, 50, 1000, 0, 100)
    if(percent > 100): percent = 100
    if(percent < 0): percent = 0
    color = percent_to_rgb(100 - percent)

    print(str(distance) + "mm --> " + str(percent) + "%")

    robot.led.set_led("all", color[0], color[1], color[2])

distanceSensor.unsub_distance()
robot.close()