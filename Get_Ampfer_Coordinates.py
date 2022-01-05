import math
from haversine import inverse_haversine
import xml.etree.ElementTree as ET
from exif import Image

IMG_DIR = "Images"
AMPFER_DIR = "AMPFER"
ANGLE_OF_VIEW = 78.8
PIXEL_PER_DEGREE = 63.45177664974619
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
        image = Image(img_text)
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
    x -= 2000
    y -= 1500
    dist = 0
    if x != 0 and y != 0:
        dist = math.sqrt(pow(x, 2) + pow(y, 2))
    return dist / PIXEL_PER_DEGREE, math.atan2(y - 1500, x - 2000) + math.pi / 2


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ampfer_list = []
    for child in root:
        if child.tag == "object":
            avgx = int((int(child[4][0].text) + int(child[4][2].text)) / 2)
            avgy = int((int(child[4][1].text) + int(child[4][3].text)) / 2)
            ampfer_list.append((avgx, avgy))
    return ampfer_list


def get_Ampfer_Cords(index):
    IMG_PATH = f"Images/{index}.JPG"
    XML_PATH = f"Ampfer/{index}.xml"
    ampfer_coords = []
    yaw, alt, coords = get_flight_yaw_altitude_coords(f"Images/{index}.JPG")

    for x, y in parse_xml(XML_PATH):
        angle_from_camera, angle_from_middle = get_Angle_from_Camera(x, y)
        abs_angle = math.radians(yaw) + angle_from_middle # TODO OBACHT HIER -PI
        dist = alt * math.tan(math.radians(angle_from_camera))
        print(yaw)
        ampfer_coords.append(inverse_haversine(coords, dist / 1000, abs_angle))
    return ampfer_coords


if __name__ == '__main__':



    for i in range(108,112):
        print(f"{get_Ampfer_Cords(i)}  {i}")
    i = 226
    print(f"{get_Ampfer_Cords(i)=}  {i}")
