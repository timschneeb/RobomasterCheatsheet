import time
import cv2
from robomaster import robot
from actions import FollowLine

ep_robot = robot.Robot()

if __name__ == '__main__':
    #ep_robot.initialize(conn_type="sta", sn="3JKDH63001E06B")
    ep_robot.initialize(conn_type="ap")

    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False)

    # 200x ein Bild vom Roboter abrufen
    for r in range(200):
        # Bild abrufen
        img = ep_camera.read_cv2_image(strategy="newest", timeout=3)
    
        for i in range(0,1280,30):
            # Statischer Horizont (repräsentiert durch Punkte) auf Bild zeichnen
            cv2.circle(img, [int(i), int(720/2)], 3, [255, 255, 255], -1)

        # Fertiges Bild als Fenster anzeigen
        cv2.imshow("Linie", img)
        cv2.waitKey(1)

        # 100ms warten
        time.sleep(0.1)
        
    # Videostream beenden
    ep_camera.stop_video_stream()

    ep_robot.close()
