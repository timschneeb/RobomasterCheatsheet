<h1 align="center">
  Robomaster Cheatsheet
  <br>
</h1>
<p align="center">
  <a href="#verbindungsaufbau">Verbindungsaufbau</a> •
  <a href="#chassis-api">Chassis</a> •
  <a href="#robotic-arm-api">Robotic arm</a> •
  <a href="#gripper-api">Gripper</a> •
  <a href="#distance-sensor-api">Sensor</a> •
  <a href="#vision-api">Camera</a> •
  <a href="#led-api">LED</a>
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

### Chassis API

Kommentierte Beispielskripte:
* [Einfache Bewegungen](chassis/chassis.py)
* [Rechteck mit Drehung](chassis/rechteck.py)

| Funktion | Beschreibung |
| ------------------------------------------------------------ | ---- |
| `drive_speed(x, y, z, timeout)` | Fahre mit best. Geschwindigkeit; `x`,`y` = m/s; `z` = °/s; `timeout` = s |
| `move(x, y, z, xy_speed, z_speed)` | Fahre best. Länge;  `x`,`y` = m; `z` = Grad °; `xy_speed` = m/s; `z_speed` = °/s |
| `drive_wheels(w1, w2, w3, w4, timeout)` | Bestimme Geschwindigkeiten der Räder; `w1..w4` = rpm |

### Robotic arm API

| Funktion       | Beschreibung                        |
| -------------- | ----------------------------------- |
| `move(x, y)`   | Relative Armbewegung; `x`, `y` = mm |
| `moveto(x, y)` | Absolute Armbewegung; `x`, `y` = mm |
| `recenter()`   | Arm zur Mitte zurückbewegen         |

### Gripper API

Beispielskript, welches ein Objekt greift, transportiert und ablegt: [`gripper.py`](gripper/gripper.py)

| Funktion       | Beschreibung                         |
| -------------- | ------------------------------------ |
| `open(power)`  | Öffne Gripper; `power` = [1, 100]    |
| `close(power)` | Schließe Gripper; `power` = [1, 100] |
| `pause()`      | Stoppe Bewegung                      |


### Distance sensor API

Kommentierte Beispielskripte:
* [Infrarotsensor zum Bremsen verwenden](sensor/sensor-drive.py)
* [LEDs je nach Entfernung mithilfe eines Rot-Gelb-Grün Farbverlauf färben](sensor/sensor-led.py) (verwendet `Queue` um Daten zwischen zwei Threads asynchron auszutauschen)


| Funktion       | Beschreibung                         |
| -------------- | ------------------------------------ |
| `sub_distance(hz, cb)`  | Entfernungsdaten abonnieren; `hz` = Rate, `cb` = Callback-Funktion (Int-Array mit je 4 Werten als Parameter) |
| `unsub_distance()` | Entfernungsdaten deabonnieren|

#### Callback

Der oben-genannte `cb`-Parameter von `sub_distance` stellt eine Referenz zu einer Funktion dar. Sie erhält die Daten vom Sensor asynchron:
```python
def cb_distance(array):
    left = array[0]
    right = array[1]
    front = array[2]
    back = array[3]

```
Die Funktion nimmt ein Integer-Array als Parameter an. Das Array enthält normalerweise Entfernungsdaten für alle Seiten des Roboters. Allerdings, haben unsere Roboter nur einen Sensor an der linken Seite verbaut. Somit sind die anderen drei Werte im Array immer null.


### Vision API

Kommentierte Beispielskripte:
* [Vehalten des Roboters (sowie die LEDs) je nach Marker ändern](vision/camera-marker.py)
* [Fahrt entlang einer blauen Linie](vision/follow-line)

| Funktion       | Beschreibung                         |
| -------------- | ------------------------------------ |
| `sub_detect_info(name, color, cb)`  | Bilderkennungsdaten abonnieren; `name` = Modus (siehe Tabelle unten), `color` = Farbe der Marke/Linie, `cb` = Callback-Funktion |
| `unsub_detect_info(name)` | Bilderkennungsdaten deabonnieren; `name` = Modus  |

| Modus       | Callback-Parameter | Beschreibung                         |
| -------------- | -------------- | ------------------------------------ |
| `person`  | `[x, y, Breite, Höhe]` | Personenerkennung |
| `gesture` | `[x, y, Breite, Höhe]` | Gestenerkennung |
| `line`    | `[x, y, Tangentenwinkel (theta), Krümmung]` | Linienerkennung |
| `marker`  | `[x, y, Breite, Höhe, Name d. Markers]` | Markererkennung |
| `robot`  | `[x, y, Breite, Höhe]` | Robotererkennung |

#### Callback
Wie bei der [Distance API](#distance-sensor-api), benötigt `sub_detect_info` auch eine Referenz zu einer Callback-Funktion.

Im folgenden Beispiel wird **Linienerkennung** verwendet:

```python
    def cb_vision_line_update(line_data):
        avg_theta = 0
        avg_c = 0
        points = 0
        for d in line_data[-3:]:
            x, y, theta, c = d
            avg_theta += theta
            avg_c += c
            points += 1

        avg_theta = avg_theta / points
        avg_c = avg_c / points

```
`line_data` enthält eine Sammlung von Punkten, die eine Linie beschreiben. Jeder Punkt enthält seine x/y-Koordinaten, den Tangentenwinkel (theta) und die Krümmung (C). Der Codeauszug berechnet die Durchschnittswerte von Theta und C der letzten drei Punkte.


#### Bildübertragung

Zusätzlich können die Kamerabilder in Echtzeit vom Roboter heruntergeladen und angezeigt werden. Dazu kann man auch die `cv2` Bibliothek verwenden, um auf das Bild zu zeichnen. Beispiel:
```python
import time
import cv2
from robomaster import robot

# [...]

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
```
#### Linie erfassen

Details zu Linienerkennung sind auf [dieser Unterseite zu finden](vision/follow-line).


### LED API

| Funktion       | Beschreibung                         |
| -------------- | ------------------------------------ |
| `set_led(comp, r, g, b, effect, freq)` | Setze LED-Farbe; `comp` = Bereich, `r,g,b` = Farbe; `effect` = Lichteffekt; `freq` = Frequenz für `flash`-Effekt |

Mögliche Bereiche: `all, top_all, bottom_left, bottom_right, ...`

Mögliche Effekte: `on, off, flash, breath, scrolling`
_________

Quelle: <https://robomaster-dev.readthedocs.io/>
