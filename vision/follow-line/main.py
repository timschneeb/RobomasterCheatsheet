import time
import cv2
from robomaster import robot
from actions import FollowLine

ep_robot = robot.Robot()

if __name__ == '__main__':
    ep_robot.initialize(conn_type="sta", sn="3JKDH63001E06B")

    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False)

    follow = FollowLine(ep_robot)
    follow.begin()

    for i in range(0, 100):
        vision_data = follow.get_last_data()
        if vision_data is None:
            time.sleep(0.5)
            print("Noch nicht bereit")
            continue

        img = ep_camera.read_cv2_image(strategy="newest", timeout=3)

        number = len(vision_data)
        line_type = vision_data[0]
        # print('line_type', line_type)

        for j in range(1, number):
            x, y, theta, c = vision_data[j]
            # print(vision_data[j])
            cv2.circle(img, [int(x * 1280), int(y * 720)], 3, [255, 255, 255], -1)

        cv2.imshow("Linie", img)
        cv2.waitKey(1)

    follow.end()
    ep_camera.stop_video_stream()

    ep_robot.close()
