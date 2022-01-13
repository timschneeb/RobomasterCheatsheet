<h1 align="center">
  Robomaster Cheatsheet
  <br>
</h1>
<p align="center">
  <a href="#verbindungsaufbau">Verbindungsaufbau</a> •
  <a href="#robot-api">Robot</a> •
  <a href="#chassis-api">Chassis</a> •
  <a href="#robotic-arm-api">Robotic arm</a> •
  <a href="#gripper-api">Gripper</a>
</p>


## Verbindungsaufbau

```python
from robomaster import robot

if __name__ == '__main__':
    robot = robot.Robot()
    robot.initialize(conn_type="sta", sn="3JKDH2T001ULTD")
	# [...]
    robot.close()
```

## Schnittstellen

### Robot API

| Objekte             |
| ------------------- |
| `robot.chassis`     |
| `robot.robotic_arm` |
| `robot.gripper`     |

### Chassis API

| Funktion | Beschreibung |
| ------------------------------------------------------------ | ---- |
| ```drive_speed(x, y, z, timeout)``` | Fahre mit best. Geschwindigkeit; `x`,`y`,`z` = m/s; `timeout` = s |
| `move(x, y, z, xy_speed, z_speed)` | Fahre best. Länge;  `x`,`y` = m; `z` = Grad °; `xy_speed` = m/s; `z_speed` = °/s |
| `drive_wheels(w1, w2, w3, w4, timeout)` | Bestimme Geschwindigkeiten der Räder; `w1..w4` = rpm |

### Robotic arm API

| Funktion       | Beschreibung                        |
| -------------- | ----------------------------------- |
| `move(x, y)`   | Relative Armbewegung; `x`, `y` = mm |
| `moveto(x, y)` | Absolute Armbewegung; `x`, `y` = mm |
| `recenter()`   | Arm zur Mitte zurückbewegen         |

### Gripper API

| Funktion       | Beschreibung                         |
| -------------- | ------------------------------------ |
| `open(power)`  | Öffne Gripper; `power` = [1, 100]    |
| `close(power)` | Schließe Gripper; `power` = [1, 100] |
| `pause()`      | Stoppe Bewegung                      |

