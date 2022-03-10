from unittest import case
from scipy import interpolate
import numpy
from robomaster import robot, vision, chassis
import time

robot = robot.Robot()

lastRectInfo = []
scannedMarkers = []
stopMove = False
handlerLocked = False
speed = 30 #rpm

def get_symbol_from_rect(rect_info):
    if len(rect_info) < 1 or len(rect_info[0]) < 5:
        return ""
    return rect_info[0][4]

def get_x_from_rect(rect_info):
    if len(rect_info) < 1 or len(rect_info[0]) < 5:
        return 0
    return rect_info[0][0]

def handle_symbol(rect_info):
    global robot, speed
    handlerLocked = True
    symbol = get_symbol_from_rect(rect_info)



    if symbol in scannedMarkers:
        print("Marker '" + symbol + "' bereits gescannt. Überspringe..")
        handlerLocked = False
        return

    if symbol == "":
        handlerLocked = False
        return

    print(symbol)

    if(symbol == "2"):
        robot.chassis.drive_wheels(0, 0, 0, 0)
        time.sleep(4)
        robot.chassis.drive_wheels(-speed, speed, -speed, speed)
    elif(symbol == "heart"):
        robot.chassis.drive_wheels(0, 0, 0, 0)
        robot.led.set_led("all", 255, 0, 0)
        time.sleep(4)
        robot.led.set_led("all", 255, 255, 255)
        time.sleep(1)
        robot.chassis.drive_wheels(-speed, speed, -speed, speed)
        time.sleep(3)
        robot.chassis.drive_wheels(0,0,0,0)

        stopMove = True
    
    scannedMarkers.append(symbol)

    handlerLocked = False


def cb_vision(rect_info):
    global robot, lastRectInfo
    #if len(rect_info) > 0:
    #    print(rect_info)
    #    return

    x = get_x_from_rect(rect_info)

    if not(x > 0.42 and x < 0.56):
        return

    if get_symbol_from_rect(rect_info) == get_symbol_from_rect(lastRectInfo):
        lastRectInfo = rect_info
        return # Keine Änderung des Symbols

    if not handlerLocked:
        handle_symbol(rect_info)

    lastRectInfo = rect_info

if __name__ == '__main__':
    robot.initialize(conn_type="sta", sn="3JKDH6U001MTUX")
    #robot.initialize(conn_type="ap")
	
    chassis = robot.chassis
    visionSensor = robot.vision
    visionSensor.sub_detect_info("marker", "red", cb_vision)

    chassis.drive_wheels(-speed, speed, -speed, speed)
        
    while not stopMove:
        time.sleep(0.1)
    
    chassis.drive_wheels(0, 0, 0, 0)
    visionSensor.unsub_detect_info("marker")
    robot.close()
