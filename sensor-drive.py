from robomaster import robot
import time

robot = robot.Robot()

def translate(value, leftMin, leftMax, rightMin, rightMax):
    return rightMin + (float(value - leftMin) / float(leftMax - leftMin) * rightMax - rightMin)

def cb_distance(val):
    global robot
    left = val[0]

    speed = translate(left, 0, 3200, 60, 200)

    # Falls weniger als 40cm entfernt sofort stoppen
    if left < 40:
        speed = 0

    print(str(left) + "cm --> " + str(speed) + "rpm")
    robot.chassis.drive_wheels(-speed, speed, -speed, speed)

if __name__ == '__main__':
    robot.initialize(conn_type="sta", sn="3JKDH63001E06B")
	
    distanceSensor = robot.sensor
    # cb_distance 5mal pro Sekunde mit Entfernungsdaten versorgen
    distanceSensor.sub_distance(5, cb_distance)

    # Programm nach 20 Sekunden stoppen
    time.sleep(20)

    distanceSensor.unsub_distance()
    robot.close()
