import time
from robomaster import robot

ep_robot = robot.Robot()

def move_gripper(robot, x, y, open):
    arm = robot.robotic_arm
    
    time.sleep(1)
    arm.move(x, 0).wait_for_completed()
    arm.move(0, -y).wait_for_completed()

    if open: 
        robot.gripper.open(power=50)
    else:
        robot.gripper.close(power=50)

    time.sleep(1)
    robot.gripper.pause()

    arm.move(0, y).wait_for_completed()
    arm.move(-x, 0).wait_for_completed()    

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

    chassis.move(2, 0, 0, xy_speed=1).wait_for_completed()
    move_gripper(ep_robot, 50, 50, False)
    chassis.move(-2, 0, 0, xy_speed=1).wait_for_completed()
    move_gripper(ep_robot, 50, 50, True)

    ep_robot.close()
