from robomaster import robot
import time

ep_robot = robot.Robot()
xy_speed = 1/2 # m/s
z_speed = 90/2 # m/s

if __name__ == '__main__':
    #ep_robot.initialize(conn_type="sta", sn="3JKDH6U0011J02")
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis

    for i in range(4):
        # 1 Meter nach vorne
        ep_chassis.move(1, 0, 0, xy_speed).wait_for_completed()
        time.sleep(50)
        # 90° Drehung
        ep_chassis.move(0, 0, 90, 0, z_speed).wait_for_completed()
    
    ep_robot.close()
