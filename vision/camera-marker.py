from robomaster import robot, vision, chassis
import time

robot = robot.Robot()

lastRectInfo = []
scannedMarkers = []
stopMove = False
handlerLocked = False
speed = 30 #rpm

# Funktion, um Symbolname aus Array sicher zu laden
def get_symbol_from_rect(rect_info):
    if len(rect_info) < 1 or len(rect_info[0]) < 5:
        return ""
    return rect_info[0][4]

# Funktion, um x-Koord. aus Array sicher zu laden
def get_x_from_rect(rect_info):
    if len(rect_info) < 1 or len(rect_info[0]) < 5:
        return 0
    return rect_info[0][0]

def handle_symbol(rect_info):
    global robot, speed
    handlerLocked = True
	
    symbol = get_symbol_from_rect(rect_info)

    # Prüfe, ob Symbol bereits gescannt wurde
    if symbol in scannedMarkers:
        print("Marker '" + symbol + "' bereits gescannt. Überspringe..")
        handlerLocked = False
        return

    # Überspringe, falls kein Symbol erkannt
    if symbol == "":
        handlerLocked = False
        return

    print(symbol)

    # Verhalten des Roboters je nach Marker ändern
    if(symbol == "2"):
	# 4 Sekunden pausieren
        robot.chassis.drive_wheels(0, 0, 0, 0)
        time.sleep(4)
        robot.chassis.drive_wheels(-speed, speed, -speed, speed)
    elif(symbol == "heart"):
	# Pausieren + LEDs für 4s auf rot setzen, dann 3s weiter fahren und Programm beenden
        robot.chassis.drive_wheels(0, 0, 0, 0)
        robot.led.set_led("all", 255, 0, 0)
        time.sleep(4)
        robot.led.set_led("all", 255, 255, 255)
        time.sleep(1)
        robot.chassis.drive_wheels(-speed, speed, -speed, speed)
        time.sleep(3)
        robot.chassis.drive_wheels(0,0,0,0)

        stopMove = True
    
    # Gescannter Marker in Array speichern
    scannedMarkers.append(symbol)

    handlerLocked = False

# Vision callback
def cb_vision(rect_info):
    global robot, lastRectInfo

    x = get_x_from_rect(rect_info)
    # Prüfe, ob Marker ungefähr in der Mitte des Sichtfeldes liegt
    if not(x > 0.42 and x < 0.56):
        return

    # Prüfe, ob sich das Symbol geändert hat
    if get_symbol_from_rect(rect_info) == get_symbol_from_rect(lastRectInfo):
        lastRectInfo = rect_info
        return # Keine Änderung des Symbols

    # Daten verarbeiten, falls handle_symbol bereit
    if not handlerLocked:
        handle_symbol(rect_info)

    # Speichere rect_info für nächsten Zyklus
    lastRectInfo = rect_info

if __name__ == '__main__':
    robot.initialize(conn_type="sta", sn="3JKDH6U001MTUX")
	
    chassis = robot.chassis
    visionSensor = robot.vision
    visionSensor.sub_detect_info("marker", "red", cb_vision)

    # Beginne seitlich zu fahren
    chassis.drive_wheels(-speed, speed, -speed, speed)
        
    while not stopMove:
        time.sleep(0.1)
    
    chassis.drive_wheels(0, 0, 0, 0)
    visionSensor.unsub_detect_info("marker")
    robot.close()
