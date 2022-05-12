from robomaster import robot

if __name__ == '__main__':
    # Verbindungsaufbau
    robot = robot.Robot()
    robot.initialize(conn_type="sta", sn="3JKDH2T001ULTD")
	 
    chassis = robot.chassis
    
    # Bewege 1m nach vorne mit 0.5m/s und warte vor dem nächsten Befehl
    chassis.move(1, 0, 0, 0.5).wait_for_completed()
    
    # Drehe um 90° mit 15°/s in 6 Sekunden und warte vor dem nächsten Befehl
    chassis.move(0, 0, 90, 0, 15).wait_for_completed()
    
    # Drehe um 90° zurück innerhalb von 4 Sekunden mit `drive_speed()`
    chassis.drive_speed(0, 0, -90/4, 4)
    time.sleep(4);
    
    # Verbindung schließen
    robot.close()
