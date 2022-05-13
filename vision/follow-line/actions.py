import math
import time
from scipy import interpolate
from threading import Lock
from abc import abstractmethod

import calc
from stack import ActionStack

class BaseAction:
    @abstractmethod
    def undo(self):
        pass

    @staticmethod
    def is_checkpoint():
        return False


class Checkpoint(BaseAction):
    @staticmethod
    def is_checkpoint():
        return True

    def undo(self):
        pass


class SyncAction(BaseAction):
    @abstractmethod
    def exec(self):
        pass


class AsyncAction(BaseAction):
    @abstractmethod
    def begin(self):
        pass

    @abstractmethod
    def end(self):
        pass


class DriveSpeedAction(AsyncAction):
    def __init__(self, robot, x=0.0, y=0.0, z=0.0):
        self.robot = robot
        self.speeds = [x, y, z]
        self.start_time = 0
        self.duration = 0

    def begin(self):
        # Aktuelle Zeit
        self.start_time = time.time()
        self.robot.chassis.drive_speed(self.speeds[0], self.speeds[1], self.speeds[2])
        pass

    def end(self):
        # Zeitdifferenz
        self.duration = time.time() - self.start_time
        self.robot.chassis.drive_wheels(0, 0, 0, 0)
        pass

    def undo(self):
        self.robot.chassis.drive_speed(-self.speeds[0], -self.speeds[1], -self.speeds[2])
        time.sleep(self.duration)
        self.robot.chassis.drive_wheels(0, 0, 0, 0)


class MoveDistanceSyncAction(SyncAction):
    def __init__(self, robot, x=0.0, y=0.0, z=0.0, xy_speed=0.0, z_speed=0.0):
        self.robot = robot
        self.coords = [x, y, z]
        self.speeds = [xy_speed, z_speed]

    def undo(self):
        self.robot.chassis.move(self.coords[0], self.coords[1], self.coords[2], self.speeds[0], self.speeds[1])\
            .wait_for_completed()

    def exec(self):
        self.robot.chassis.move(-self.coords[0], -self.coords[1], -self.coords[2], self.speeds[0], self.speeds[1])\
            .wait_for_completed()


class FollowLine(AsyncAction):
    def __init__(self, robot):
        self.lock = Lock()
        self.active = False
        self.stack = ActionStack()
        self.robot = robot
        self.last_action = None
        self.last_vision = None
        

    def begin(self):
        self.active = True
        if self.robot is None:
            # Testmodus ohne Robotersteuerung
            print("FollowLine: Robot nicht definiert")
        else:
            self.robot.vision.sub_detect_info(name="line", color="blue", callback=self.vision_update)

    def get_last_data(self):
        return self.last_vision

    def end(self):
        self.active = False
        self.robot.vision.unsub_detect_info("line")
        
        # Letzter Befehl stoppen und auf Stack legen
        if self.last_action is not None:
            self.last_action.end()
            self.stack.push(self.last_action)

    def checkIfSpeedsApproxEqual(self, s):
        if self.last_action is None:
            return False

        for i in range(0,2):
            close = math.isclose(s[i], self.last_action.speeds[i], abs_tol=0.21)
            if not close:
                return False
        return True

    def vision_update(self, vision_data):
        # Ignorieren, falls Bereich noch gesperrt oder falls abgebrochen
        if not self.active or self.lock.locked():
            print("FollowLine: Übersprungen!")
            return

        # Bereich sperren
        self.lock.acquire()
        self.last_vision = vision_data

        next_x = 0.5
        avg_theta = 0
        avg_c = 0
        points = 0
        i = 0
        # Letzte drei Punkte aus vision_data auswählen (falls vorhanden) und Durchschnitte berechnen
        # Evtl. kann man bessere Ergebnisse erzielen, wenn stattdessen die *ersten* drei Pkte. betrachtet werden
        for d in vision_data[-3:]:
            x, y, theta, c = d

            # x-Koord. des zweiten Pkts. wird als Ankerpunkt für die y-Nachjustierung ausgewählt
            if i == 1:
                next_x = x

            avg_theta += theta
            avg_c += c
            points += 1
            i += 1

        if points < 1:
            # Noch weiter nach vorne fahren, keine Linie
            x_spd = 0.5
            avg_theta = 0
            avg_c = 0
        else:
            # Mit konstanter Geschwindigkeit nach vorne
            x_spd = 0.5
            avg_theta = avg_theta / points
            avg_c = avg_c / points

        # Falls nächste x-Koord. fast aus Sichtfeld, seitlich nachjustieren
        side_speed_map_old = [
            [+0.0,  +0.3, +0.38, 0.4, 0.5],  # x-Koord. d. Pkte.
            [-0.75, -0.5, -0.25, 0.0, 0.0]   # seitl. Geschwindigk. (y)
        ]
        side_speed_map = [
            [+0.0,  +0.2, 0.3, 0.4, 0.5],  # x-Koord. d. Pkte.
            [-0.75, -0.3, 0.0, 0.0, 0.0]   # seitl. Geschwindigk. (y)
        ]
        # Skalen spiegeln ([0.0;0.5] auf [0.5;1.0] spiegeln)
        x_coord_map = side_speed_map[0].copy()
        x_coord_map.reverse()
        x_coord_map = [1 - x for x in x_coord_map]
        side_speed_map[0] += x_coord_map

        y_speed_map = side_speed_map[1].copy()
        y_speed_map.reverse()
        y_speed_map = [-y for y in y_speed_map]
        side_speed_map[1] += y_speed_map

        # y-Geschwindigkeit in Abhängigkeit zu x-Koord. bestimmen
        y_speed_func = interpolate.interp1d(side_speed_map[0], side_speed_map[1])
        y_spd = y_speed_func(next_x).flat[0]

        # Drehgeschw. berechnen; Vorzeichen von C auf Theta übernehmen
        z_spd_full = math.copysign(avg_theta, avg_c)

        # TODO
        #y_spd = 0
        #x_spd = 0
        #z_spd = 0

        # Geschwindigkeitslimit
        y_spd = max(-3.0, min(3.0, y_spd))
        z_spd = max(-90, min(90, z_spd_full))

        approxEqual = self.checkIfSpeedsApproxEqual([x_spd, y_spd, z_spd])
        
        print(f"{'* ' if approxEqual else ''}Avg-Theta: {str(round(avg_theta, 2))}°;\t"
              f"Avg-C: {str(round(avg_c, 2))}; \t"
              f"Z: {str(round(z_spd_full, 2))}°/s \t"
              f"=> Z (limit): {str(round(z_spd, 2))}°/s\t"
              f"||\tY: {str(round(y_spd, 2))}m/s\t"
              f"||\tX: {str(round(x_spd, 2))}m/s")

        if approxEqual:
            # Letzter Befehl ist ungefähr identisch
            self.lock.release()
            return

        if self.robot is None:
            # Testmodus ohne Robotersteuerung
            self.lock.release()
            return

        if self.last_action is not None:
            # Letzter Befehl stoppen und auf Stack legen
            self.last_action.end()
            self.stack.push(self.last_action)
            self.last_action = None

        # Neuen Fahr-Befehl starten
        action = DriveSpeedAction(self.robot, x_spd, y_spd, z_spd)
        action.begin()
        self.last_action = action

        # Bereich entsperren
        self.lock.release()

    def undo(self):
        self.stack.undo_all()


