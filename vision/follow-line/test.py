import time

from actions import FollowLine

dataset = [
    0, # Linientyp
    [0.496875, 0.7944444, 4.617569, 0.0],
    [0.50625, 0.6777778, 15.5778351, 0.3653422],
    [0.534375, 0.5611112, 34.9020844, 0.6522604],
    [0.596875, 0.4777778, 58.3318939, 0.7954884],
    [0.6625, 0.45, 83.490715, 0.8563049],
    [0.728125, 0.4444444, 90.0, 0.2360052],
    [0.79375, 0.4444444, 72.3040161, -0.5846216],
    [0.859375, 0.4333333, 54.1583939, -0.6178457],
    [0.925, 0.3944445, 23.7711563, -1.0266379],
    [0.884375, 0.3166667, 5.9792786, -0.6158768],
    # x      , y        , theta,   , c
]

# Testskript mit festem Datensatz ohne Roboter
follow = FollowLine(None)
follow.begin()
# Initialer Datensatz eingeben
follow.vision_update(dataset)
while len(dataset) >= 3:
    # Bearbeitete Reihe (=Punkt) aus dem Datensatz löschen
    del dataset[1]
    # Datensatz wieder eingeben (nächster Punkt/Reihe)
    follow.vision_update(dataset)
    time.sleep(0.2)

