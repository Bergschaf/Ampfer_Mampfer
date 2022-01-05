import math
import os

import haversine
from haversine import inverse_haversine
import xml.etree.ElementTree as ET
from exif import Image as EImage
import webbrowser

IMG_DIR = "DJI_0723"
AMPFER_DIR = "DJI_0723"
ANGLE_OF_VIEW = 78.8

# Ackerbohnen einfahrt links oben: 568146,92 5320710,78
# Fußballtor Schwimmhallenseite: 571192,76 5323946,60
# Schulhaus Eck beim Sonnensegel: 571143,07 5323920,79
# Schwimmhalle Eck beim Sfz Eingang: 571170,33 5323948,68
# Eck Sportplatz beim Schwimmhallen Eingang: 571220,89 5323959,95
# Eck Gemeindehalle beim Sportplatz: 571149,63 5323946,35
# Eck Gemeindehalle Richtung Haupteingang: 571142,76 5323963,14
# Einfahrt Ackerbohen mit Baum, rechts an der Straße: 568278,04 5320626,69


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def get_flight_yaw_altitude_coords(image_path):
    with open(image_path, "rb") as img:

        img_text = img.read()
        image = EImage(img_text)
        coords = (decimal_coords(image.gps_latitude,
                                 image.gps_latitude_ref),
                  decimal_coords(image.gps_longitude,
                                 image.gps_longitude_ref))

        start_pos = img_text.find(b"FlightYawDegree=") + 17
        for i, b in enumerate(img_text[start_pos:]):
            if b == 34:
                end_pos = i
                break
        yaw = float(img_text[start_pos:end_pos + start_pos])
        start_pos = img_text.find(b"RelativeAltitude=") + 18
        for i, b in enumerate(img_text[start_pos:]):
            if b == 34:
                end_pos = i
                break
        alt = float(img_text[start_pos:end_pos + start_pos])
        return yaw, alt, coords


def get_Angle_from_Camera(x: int, y: int):
    new_x = x - 2000
    new_y = y - 1500
    dist = 0
    if new_x != 0 and new_y != 0:
        dist = math.sqrt(pow(new_x, 2) + pow(new_y, 2))
    return dist, math.atan2(y - 1500, x - 2000) + math.pi / 2 # TODO DOK pi / 2 weil nullpunkt sonst an falcher stelle


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ampfer_list = []
    for child in root:
        if child.tag == "object":
            avgx = int((int(child[4][0].text) + int(child[4][2].text)) / 2)
            avgy = int((int(child[4][1].text) + int(child[4][3].text)) / 2)
            ampfer_list.append((avgx, avgy, child[0].text))
    return ampfer_list


def get_Ampfer_Cords(filename):
    IMG_PATH = f"{IMG_DIR}/{filename}.JPG"
    XML_PATH = f"{AMPFER_DIR}/{filename}.xml"
    ampfer_coords = []
    yaw, alt, coords = get_flight_yaw_altitude_coords(IMG_PATH)
    meter_per_pixel = (alt * math.tan(math.radians(39.5)))/math.sqrt(pow(2000,2)+pow(1500,2))
    for x, y, name in parse_xml(XML_PATH):
        dist_pixel, angle_from_middle = get_Angle_from_Camera(x, y)
        abs_angle = math.radians(yaw) + angle_from_middle

        dist = dist_pixel * meter_per_pixel

        ampfer_coords.append((inverse_haversine(coords, dist, abs_angle, unit=haversine.Unit.METERS), name, math.degrees(angle_from_middle)))
    return ampfer_coords,coords


if __name__ == '__main__':
    for f in os.listdir("DJI_0723"):
        if f[-4:].lower() == ".jpg":
            print(f)
            #img = IMG.open("DJI_0723/"+f)
            #img.show()
            x = input("")
            if x == "n":
                continue
            coords,drone = get_Ampfer_Cords(f[:-4])
            print(coords)
            for i in coords:
                if False:
                    webbrowser.open_new_tab(f"https://earth.google.com/web/search/{i[0][0]}+{i[0][1]}")
                    print(f, i[0],i[2],i[1])
                    x = input("")
                    if x == "exit":
                        exit(42)
