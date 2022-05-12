import time
from robomaster import robot

ep_robot = robot.Robot()

# Funktion, welche den Gripper öffnet/schließt und den Arm dabei um x & y bewegt
def move_gripper(robot, x, y, open):
    arm = robot.robotic_arm
    
    time.sleep(1)
    # Arm bewegen
    arm.move(x, 0).wait_for_completed()
    arm.move(0, -y).wait_for_completed()

    # Gripper öffnen/schließen
    if open: 
        robot.gripper.open(power=50)
    else:
        robot.gripper.close(power=50)

    time.sleep(1)
    robot.gripper.pause()

    # Arm zurück bewegen
    arm.move(0, y).wait_for_completed()
    arm.move(-x, 0).wait_for_completed()    

# Funktion, um den Arm und Gripper in Eingangsposition zu bewegen
def reset_gripper(robot):
    robot.gripper.open(power=50)
    time.sleep(1)
    robot.gripper.pause()
    robot.robotic_arm.recenter()
    time.sleep(2)

if __name__ == '__main__':
    # ep_robot.initialize(conn_type="sta", sn="3JKDH63001E06B")
    ep_robot.initialize(conn_type="ap")

    chassis = ep_robot.chassis

    reset_gripper(ep_robot)

    # 2m nach vorne fahren
    chassis.move(2, 0, 0, xy_speed=1).wait_for_completed()
    # Gegenstand greifen
    move_gripper(ep_robot, 50, 50, False)
    # 2m nach hinten fahren
    chassis.move(-2, 0, 0, xy_speed=1).wait_for_completed()
    # Gegenstand loslassen
    move_gripper(ep_robot, 50, 50, True)

    ep_robot.close()
