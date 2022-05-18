import math
import time
from scipy import interpolate
from threading import Lock
from abc import abstractmethod
from library.pid import PID

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
        self.last_error = 0
        self.pid_val = [0, 0, 0]
        self.last_pid = 0
        self.pid = PID(115, 0, 12, setpoint=0.5, sample_time=0.1) # <- TODO
        self.update_time = 100
        self.last_update = 0

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
        # Erste drei Punkte aus vision_data auswählen (falls vorhanden) und Durchschnitte berechnen
        # Notiz: Erstes Element in vision_data ist line_type (int) und muss ignoriert werden
        # Evtl. kann man bessere Ergebnisse erzielen, wenn stattdessen die unter bestimmten Bedingungen die letzten drei Pkte. betrachtet werden
        for d in vision_data[1:4]: # Um letzte 3 Pkt. zu betrachten: "for d in vision_data[-3:]:"
            x, y, theta, c = d

            # x-Koord. des zweiten Pkts. wird als Ankerpunkt für die y-Nachjustierung ausgewählt
            if i == 1:
                next_x = x

            avg_theta += theta
            avg_c += c
            points += 1
            i += 1

        if points < 1:
            # Noch weiter nach vorne fahren, keine Linie sichtbar
            x_spd = 0.5
            avg_theta = 0
            avg_c = 0
        else:
            # Mit konstanter Geschwindigkeit nach vorne
            x_spd = 0.5
            avg_theta = avg_theta / points
            avg_c = avg_c / points

        now = int(round(time.time() * 1000))
        time_diff = now - self.last_update

        if time_diff < self.update_time:
            print("PID: Cooldown2")
            self.lock.release()
            return

        output = -1 * self.pid(next_x) # TODO Output invertieren?
        if output == self.last_pid:
            print("PID: Cooldown")
            self.lock.release()
            return
        else:
            self.last_pid = output


        #error = next_x - 0.5 # 0.5 - x

        #self.pid_val[0] = error # P
        #self.pid_val[1] += error # I
        #self.pid_val[2] = error - self.last_error # D
        #self.last_error = error

        Kp = 115
        Ki = 0
        Kd = 5
        #output = self.pid_val[0] * Kp + self.pid_val[1] * Ki + self.pid_val[2] * Kd


        # TODO
        y_spd = 0
        x_spd = 0.5

        # Geschwindigkeitslimit
        z_spd = max(-90, min(90, output))

        print(f"X: {str(round(next_x, 2))}; \t"
              f"PID: {str(round(output, 2))}°/s \t"
              f"=> Z (limit): {str(round(z_spd, 2))}°/s\t"
              f"||\tY: {str(round(y_spd, 2))}m/s\t"
              f"||\tX: {str(round(x_spd, 2))}m/s")

        if self.robot is None:
            # Testmodus ohne Robotersteuerung
            self.lock.release()
            return

        self.last_update = now

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


